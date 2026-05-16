"""PostgreSQL-only database helpers for VitalFlow.

This module centralizes connection handling, raw SQL execution, and basic
transaction support for the entire repository. SQLite fallbacks have been
removed so every runtime path uses the same PostgreSQL database.
"""

from __future__ import annotations

import os
from contextlib import suppress
from typing import Any, Optional

from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
import streamlit as st

from logger_config import db_logger, logger, perf_logger

load_dotenv('.env', override=False)


class DatabaseConfig:
    """Database configuration management for PostgreSQL only."""

    def __init__(self) -> None:
        self.db_type = "postgresql"
        self.connection_string = self._build_connection_string()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)

    def _get_db_url_candidate(self) -> Optional[str]:
        """Return the first configured PostgreSQL connection string, if any."""
        for key in ("DB_URL", "DATABASE_URL", "SUPABASE_DB_URL"):
            with suppress(Exception):
                value = st.secrets.get(key, "")
                if value:
                    return value

        for key in ("DB_URL", "DATABASE_URL", "SUPABASE_DB_URL"):
            value = os.getenv(key)
            if value:
                return value

        return None

    def _build_connection_string(self) -> str:
        db_url = self._get_db_url_candidate()
        if db_url:
            return db_url
        raise ValueError(
            "PostgreSQL database URL not found. Set DB_URL in .env or Streamlit secrets."
        )

    def _create_engine(self):
        engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_recycle=3600,
            pool_pre_ping=True,
            echo=False,
            isolation_level="READ COMMITTED",
            connect_args={"connect_timeout": 10},
        )

        statement_timeout_ms = int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "15000"))
        lock_timeout_ms = int(os.getenv("DB_LOCK_TIMEOUT_MS", "5000"))

        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            db_logger.logger.debug("Database connection established")
            try:
                with dbapi_conn.cursor() as cur:
                    cur.execute("SET statement_timeout = %s", (statement_timeout_ms,))
                    cur.execute("SET lock_timeout = %s", (lock_timeout_ms,))
            except Exception as exc:
                logger.warning(f"Failed to configure connection timeouts: {exc}")

        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            db_logger.logger.debug("Connection returned to pool")

        return engine

    def get_session(self) -> Session:
        return self.SessionLocal()

    def close_engine(self) -> None:
        self.engine.dispose()


try:
    db_config = DatabaseConfig()
    logger.info("Database initialized: POSTGRESQL")
except Exception as exc:
    logger.error(f"Failed to initialize database: {exc}")
    db_config = None


def get_db_connection() -> Optional[Any]:
    """Get a PostgreSQL DB-API connection from the SQLAlchemy engine."""
    try:
        if db_config is None:
            logger.error("Database not initialized")
            return None
        return db_config.engine.raw_connection()
    except Exception as exc:
        logger.error(f"Failed to get database connection: {exc}")
        return None


def get_db_session() -> Optional[Session]:
    """Get a SQLAlchemy session."""
    try:
        if db_config is None:
            logger.error("Database not initialized")
            return None
        return db_config.get_session()
    except Exception as exc:
        logger.error(f"Failed to get database session: {exc}")
        return None


def execute_raw_query(query: str, params: tuple = (), fetch_one: bool = False) -> Optional[Any]:
    """Execute one SQL statement and return rows when the statement produces them."""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return None
        conn.autocommit = False

        with conn:
            with conn.cursor() as cur:
                cur.execute(query.replace("?", "%s"), params)
                if cur.description is None:
                    return None
                return cur.fetchone() if fetch_one else cur.fetchall()
    except Exception as exc:
        logger.error(f"Query execution failed: {exc}\nQuery: {query[:120]}...")
        if conn:
            try:
                conn.rollback()
            except Exception as rollback_exc:
                logger.warning(f"Failed to rollback transaction: {rollback_exc}")
        return None
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to close database connection: {e}")


def execute_with_transaction(operations: list, description: str = "Transaction") -> bool:
    """Execute multiple SQL statements atomically."""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            return False

        conn.autocommit = False
        with conn:
            with conn.cursor() as cur:
                for query, params in operations:
                    cur.execute(query.replace("?", "%s"), params)
        logger.info(f"Transaction successful: {description}")
        db_logger.log_query("TRANSACTION", "Multiple", len(operations), "System")
        return True
    except Exception as exc:
        logger.error(f"Transaction failed: {exc}")
        if conn:
            try:
                conn.rollback()
            except Exception as rollback_exc:
                logger.warning(f"Failed to rollback transaction: {rollback_exc}")
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception as e:
                logger.warning(f"Failed to close database connection: {e}")
