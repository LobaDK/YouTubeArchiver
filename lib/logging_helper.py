"""
This module provides classes and functions for managing logging in Python applications.

It includes functionality to check if a logger exists, create a logger with a file handler and a stream handler,
and create file and stream handlers with specified log levels.

Classes:
    HandlerBase: A base class for handler configuration.
        Attributes:
            logger_name (str): The name of the logger.
            log_file (str): The path and name of the log file.

    FileAndStreamHandler: A class for file and stream handler configuration, inherits from HandlerBase.
        Attributes:
            file_log_level (int, optional): The log level for the file handler. Defaults to logging.INFO.
            stream_log_level (int, optional): The log level for the stream handler. Defaults to logging.ERROR.

    TimedRotatingFileAndStreamHandler: A class for timed rotating file and stream handler configuration, inherits from FileAndStreamHandler.
        Attributes:
            interval (str, optional): The interval at which log files should be rotated (e.g., 'midnight', 'daily', 'weekly', 'monthly'). Defaults to 'midnight'.
            backup_count (int, optional): The number of backup log files to keep. Defaults to 7.

Functions:
    logger_exists(logger_name: str) -> bool:
        Checks if a logger with the given name exists.

    create_logger(log: FileAndStreamHandler | TimedRotatingFileAndStreamHandler) -> logging.Logger:
        Creates a logger with the given name and log file.

    _create_file_handler(log_file: str, level: int) -> logging.FileHandler:
        Creates a logging FileHandler with the specified log file and level.

    _create_stream_handler(level: int) -> logging.StreamHandler:
        Creates a logging StreamHandler with the specified log level.

    _create_timed_rotating_file_handler(log_file: str, level: int, interval: str, backup_count: int) -> TimedRotatingFileHandler:
        Creates a logging TimedRotatingFileHandler with the specified log file, level, interval, and backup count.

    create_log_dir(log_dir: str):
        Creates a log directory if it does not exist.

example:
    logger = logging_helper.create_logger(
        logging_helper.FileAndStreamHandler(
            logger_name="ExampleLogger",
            log_file="example.log",
            file_log_level=logging.DEBUG,
        )
    )
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
"""

import logging
from pydantic import BaseModel
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os
from typing import Optional


class HandlerBase(BaseModel):
    logger_name: str
    log_file: str


class FileAndStreamHandler(HandlerBase):
    file_log_level: Optional[int] = logging.INFO
    stream_log_level: Optional[int] = logging.ERROR


class TimedRotatingFileAndStreamHandler(FileAndStreamHandler):
    interval: Optional[str] = "midnight"
    backup_count: Optional[int] = 7


def logger_exists(logger_name: str) -> bool:
    """
    Checks if a logger with the given name exists.

    Args:
        logger_name (str): The name of the logger to check.

    Returns:
        bool: True if a logger with the given name exists, False otherwise.
    """
    return logger_name in logging.Logger.manager.loggerDict


def create_logger(
    log: FileAndStreamHandler | TimedRotatingFileAndStreamHandler,
) -> logging.Logger:
    """
    Creates a logger with the given name and log file.

    Helper function to create, configure, and return a logger with the given name and log file.
    The logger will have a file handler and a stream handler attached to it.
    If the logger already exists, it will be returned without any changes.

    Args:
        log (FileAndStreamHandler | TimedRotatingFileAndStreamHandler): The log object containing the logger name and log file.

    Returns:
        logging.Logger: The created logger.
    """
    if not Path(log.log_file).parent.exists():
        create_log_dir(str(Path(log.log_file).parent))

    if logger_exists(log.logger_name):
        return logging.getLogger(log.logger_name)

    logger = logging.getLogger(log.logger_name)
    logger.setLevel(logging.DEBUG)

    stream_handler = _create_stream_handler(log.stream_log_level)
    logger.addHandler(stream_handler)

    if isinstance(log, FileAndStreamHandler):
        file_handler = _create_file_handler(log.log_file, log.file_log_level)
        logger.addHandler(file_handler)
    elif isinstance(log, TimedRotatingFileAndStreamHandler):
        timed_rotating_file_handler = _create_timed_rotating_file_handler(
            log.log_file,
            log.file_log_level,
            log.interval,
            log.backup_count,
        )
        logger.addHandler(timed_rotating_file_handler)

    return logger


def _create_file_handler(log_file: str, level: int) -> logging.FileHandler:
    """
    Creates a logging FileHandler with the specified log file and level.

    Args:
        log_file (str): The path and name of the log file to create.

    Returns:
        logging.FileHandler: The file handler object.

    """
    handler = logging.FileHandler(
        filename=log_file,
        encoding="utf-8",
        mode="a",
    )
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        datefmt=date_format,
        style="{",
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler


def _create_stream_handler(level: int) -> logging.StreamHandler:
    """
    Creates a logging StreamHandler with the specified log level.

    Returns:
        logging.StreamHandler: The created StreamHandler object.

    """
    handler = logging.StreamHandler()
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        datefmt=date_format,
        style="{",
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler


def _create_timed_rotating_file_handler(
    log_file: str, level: int, interval: str, backup_count: int
) -> TimedRotatingFileHandler:
    """
    Creates a logging TimedRotatingFileHandler with the specified log file, level, interval, and backup count.

    Args:
        log_file (str): The path and name of the log file to create.
        level (int): The log level for the file handler.
        interval (str): The interval at which log files should be rotated (e.g., 'midnight', 'daily', 'weekly', 'monthly').
        backup_count (int): The number of backup log files to keep.

    Returns:
        logging.handlers.TimedRotatingFileHandler: The created TimedRotatingFileHandler object.
    """
    handler = TimedRotatingFileHandler(
        filename=log_file,
        when=interval,
        backupCount=backup_count,
        encoding="utf-8",
    )
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(
        "[{asctime}] [{levelname:<8}] {name}: {message}",
        datefmt=date_format,
        style="{",
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)
    return handler


def create_log_dir(log_dir: str):
    """
    Creates a log directory if it does not exist.

    Args:
        log_dir (str): The path to the log directory.

    """
    os.makedirs(log_dir, exist_ok=True)
