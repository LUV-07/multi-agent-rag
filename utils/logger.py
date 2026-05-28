"""
utils/logger.py — Centralized logging
"""
import sys
from loguru import logger

# Remove default handler
logger.remove()

# Console handler — clean format
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> — <level>{message}</level>",
    level="DEBUG",
    colorize=True,
)

# File handler — full details
logger.add(
    "logs/rag_system.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} — {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip",
)


def get_logger(name: str):
    return logger.bind(name=name)
