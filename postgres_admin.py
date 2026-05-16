"""PostgreSQL-only setup helpers for VitalFlow.
Centralizes schema creation, blood-bank extensions, and rebuild/verification logic.
"""

from __future__ import annotations
import os
from pathlib import Path

from db_manager import get_db_connection
from logger_config import logger

PROJECT_ROOT = Path(__file__).resolve().parent

def _get_connection():
    connection = get_db_connection()
    if connection is None:
        raise RuntimeError("Database connection unavailable")
    return connection

def run_sql_file(sql_filename: str) -> None:
    """Sends the entire SQL file as one block to prevent dependency errors."""
    sql_path = PROJECT_ROOT / sql_filename
    if not sql_path.exists():
        raise FileNotFoundError(f"Missing SQL file: {sql_path}")

    connection = _get_connection()
    try:
        sql_text = sql_path.read_text(encoding="utf-8")
        cursor = connection.cursor()
        try:
            # 🚨 FIX: Execute the entire file text as one single command
            # This allows PostgreSQL to handle the internal dependencies correctly.
            cursor.execute(sql_text)
            connection.commit()
            logger.info(f"Successfully applied {sql_filename}")
        except Exception as e:
            connection.rollback()
            logger.error(f"Error applying SQL file {sql_filename}: {e}")
            raise
        finally:
            cursor.close()
    finally:
        connection.close()

def ensure_base_schema() -> None:
    """Create the core schema and blood-bank extensions."""
    run_sql_file("schema.sql")

def verify_schema() -> None:
    """Verify that all tables were created successfully."""
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        try:
            tables = (
                "roles", "hospitals", "staff", "inventory_items", 
                "hospital_inventory", "donors", "donation_records", 
                "transfer_requests", "transfer_status", "audit_logs", 
                "blood_bank", "blood_donations_override"
            )
            for table in tables:
                cursor.execute("SELECT to_regclass(%s)", (f"public.{table}",))
                if not cursor.fetchone()[0]:
                    raise RuntimeError(f"Missing table: {table}")
            logger.info("Schema verification passed")
        finally:
            cursor.close()
    finally:
        connection.close()

def _drop_vitalflow_tables() -> None:
    """Drop all VitalFlow tables so rebuild starts from a clean schema state."""
    tables = (
        "blood_donations_override", "blood_bank", "donation_records", 
        "hospital_inventory", "transfer_status", "transfer_requests", 
        "staff", "donors", "inventory_items", "hospitals", "roles", "audit_logs"
    )
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        try:
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE")
            connection.commit()
            logger.info("Dropped existing VitalFlow tables for clean rebuild")
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()

def rebuild_database() -> None:
    """Master command to wipe and recreate the database schema."""
    _drop_vitalflow_tables()
    ensure_base_schema()
    verify_schema()
    print("✅ Database schema successfully rebuilt.")