"""Centralized logging configuration for Beautiful Gradient MCP."""

import logging
import sys
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Color codes for console output
class LogColors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'

class ColoredFormatter(logging.Formatter):
    """Formatter that adds colors to console output."""

    COLORS = {
        'DEBUG': LogColors.CYAN,
        'INFO': LogColors.GREEN,
        'WARNING': LogColors.YELLOW,
        'ERROR': LogColors.RED,
        'CRITICAL': LogColors.MAGENTA,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, LogColors.RESET)
        record.levelname = f"{color}{record.levelname}{LogColors.RESET}"
        return super().format(record)

def setup_logger(name: str, log_file: str, level=logging.DEBUG) -> logging.Logger:
    """Create a logger with both file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Remove existing handlers
    logger.handlers = []

    # File handler (no colors)
    file_handler = logging.FileHandler(LOGS_DIR / log_file)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console handler (with colors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

# Create specialized loggers
oauth_logger = setup_logger("oauth", "oauth.log")
mcp_logger = setup_logger("mcp", "mcp.log")
db_logger = setup_logger("database", "database.log")
error_logger = setup_logger("error", "error.log", level=logging.ERROR)
startup_logger = setup_logger("startup", "startup.log")

# Export all loggers
__all__ = ['oauth_logger', 'mcp_logger', 'db_logger', 'error_logger', 'startup_logger']
