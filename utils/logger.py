"""Centralized logger factory for all Res-GeoAI modules."""

import logging
import sys
from typing import Optional


_loggers = {}


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    # Return a named logger with consistent format; reuse existing instances
    if name in _loggers:
        return _loggers[name]
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    log_level = getattr(logging, (level or "INFO").upper(), logging.INFO)
    logger.setLevel(log_level)
    logger.propagate = False
    _loggers[name] = logger
    return logger


def set_global_log_level(level: str):
    # Update log level across all registered loggers simultaneously
    log_level = getattr(logging, level.upper(), logging.INFO)
    for logger in _loggers.values():
        logger.setLevel(log_level)
