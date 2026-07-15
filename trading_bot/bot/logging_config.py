import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_file: str = "trading_bot.log", level: int = logging.INFO) -> logging.Logger:
    """
    Sets up logging configuration. Configures both a rotating file handler 
    and a stream handler for console output.
    """
    # Ensure log directory exists if a path is provided
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    # Formatters
    log_formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] (%(filename)s:%(lineno)d): %(message)s"
    )

    # Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear existing handlers to avoid duplicates
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # File Handler (rotating, max 5MB, keeps 3 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(level)
    root_logger.addHandler(file_handler)

    # Console Handler (clean format for CLI users)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.WARNING)  # Console shows WARNING and above by default to avoid clutter
    root_logger.addHandler(console_handler)

    logger = logging.getLogger("trading_bot")
    logger.info("Logging configured. Log file: %s", os.path.abspath(log_file))
    return logger
