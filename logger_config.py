"""
Logging Configuration Module
Centralized logging setup for VitalFlow with color output
"""

import logging
import logging.handlers
import os
from typing import Optional
import colorlog

# Create logs directory if it doesn't exist
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'vitalflow.log')
ERROR_LOG_FILE = os.path.join(LOG_DIR, 'errors.log')


def setup_logging(name: str = __name__, level: int = logging.INFO) -> logging.Logger:
    """
    Configure logging with both file and console handlers.
    
    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.hasHandlers():
        return logger
    
    # ==========================================
    # CONSOLE HANDLER (with colors)
    # ==========================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Color formatter for console
    color_formatter = colorlog.ColoredFormatter(
        fmt='%(log_color)s[%(asctime)s]%(reset)s %(levelname)-8s %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # ==========================================
    # FILE HANDLER (all logs)
    # ==========================================
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE,
        maxBytes=10_000_000,  # 10MB
        backupCount=5  # Keep 5 backup files
    )
    file_handler.setLevel(logging.DEBUG)  # Always log to file at DEBUG level
    
    file_formatter = logging.Formatter(
        fmt='[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # ==========================================
    # ERROR FILE HANDLER (errors only)
    # ==========================================
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=10_000_000,
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    return logger


# Module-level logger
logger = setup_logging(__name__)


class DatabaseLogger:
    """Specialized logger for database operations"""
    
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance
    
    def log_query(self, action: str, table: str, affected_rows: int = 0, user: str = "System"):
        """Log database query"""
        self.logger.info(f"DB[{action}] Table({table}) AffectedRows({affected_rows}) User({user})")
    
    def log_error(self, action: str, table: str, error: str, user: str = "System"):
        """Log database error"""
        self.logger.error(f"DB[{action}] Table({table}) Error({error}) User({user})")
    
    def log_transaction(self, transaction_id: str, status: str, details: str = ""):
        """Log transaction"""
        self.logger.debug(f"Transaction({transaction_id}) Status({status}) {details}")


class AuditLogger:
    """Specialized logger for audit trail"""
    
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance
    
    def log_action(self, user: str, action: str, resource: str, result: str = "SUCCESS", details: str = ""):
        """Log user action for audit trail"""
        msg = f"User({user}) Action({action}) Resource({resource}) Result({result})"
        if details:
            msg += f" Details({details})"
        self.logger.info(msg)
    
    def log_access(self, user: str, resource: str, allowed: bool):
        """Log access attempt"""
        status = "ALLOWED" if allowed else "DENIED"
        self.logger.warning(f"AccessAttempt User({user}) Resource({resource}) Status({status})")
    
    def log_data_modification(self, user: str, table: str, operation: str, record_id: any):
        """Log data modification"""
        self.logger.info(f"DataMod User({user}) Table({table}) Op({operation}) RecordID({record_id})")


class PerformanceLogger:
    """Logger for performance monitoring"""
    
    def __init__(self, logger_instance: logging.Logger):
        self.logger = logger_instance
    
    def log_query_time(self, query_name: str, duration_ms: float, rows_affected: int = 0):
        """Log query execution time"""
        if duration_ms > 1000:  # Flag slow queries (> 1 second)
            self.logger.warning(f"SLOW_QUERY {query_name} Duration({duration_ms:.2f}ms) Rows({rows_affected})")
        else:
            self.logger.debug(f"Query {query_name} Duration({duration_ms:.2f}ms) Rows({rows_affected})")
    
    def log_connection_pool_stats(self, active: int, idle: int, waiting: int):
        """Log connection pool statistics"""
        self.logger.debug(f"ConnPool Active({active}) Idle({idle}) Waiting({waiting})")


# Global logger instances
db_logger = DatabaseLogger(logger)
audit_logger = AuditLogger(logger)
perf_logger = PerformanceLogger(logger)
