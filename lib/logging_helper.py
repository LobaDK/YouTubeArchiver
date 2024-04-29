import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
import os


class LoggingHelper:
    """
    A helper class for creating and configuring loggers.

    This class provides methods to create and configure loggers with file and stream handlers.
    It also supports creating log directories and checking if a logger with a specified name exists.
    """

    def __init__(
        self,
        logger_name: str,
        log_file: str,
        include_timestamp: bool = True,
        log_level_left_padding: int = 0,
        file_log_level: int = logging.INFO,
        stream_log_level: int = logging.ERROR,
        interval: str = "midnight",
        backup_count: int = 7,
    ):
        self.logger_name = logger_name
        self.log_file = log_file
        self.include_timestamp = include_timestamp
        self.log_level_left_padding = log_level_left_padding
        self.file_log_level = file_log_level
        self.stream_log_level = stream_log_level
        self.interval = interval
        self.backup_count = backup_count

    def logger_exists(self) -> bool:
        """
        Check if the logger with the specified name exists.

        Returns:
            bool: True if the logger exists, False otherwise.
        """
        return self.logger_name in logging.Logger.manager.loggerDict

    def create_logger(self) -> logging.Logger:
        """
        Creates a logger with the given name and log file.

        Helper function to create, configure, and return a logger with the given name and log file.
        The logger will have a file handler and a stream handler attached to it.
        If the logger already exists, it will be returned without any changes.
        if the interval is specified, a TimedRotatingFileHandler will be created instead of a FileHandler.

        Returns:
            logging.Logger: The created logger.
        """
        if not Path(self.log_file).parent.exists():
            self.create_log_dir(str(Path(self.log_file).parent))

        if self.logger_exists():
            return logging.getLogger(self.logger_name)

        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)

        stream_handler = self._create_stream_handler()
        logger.addHandler(stream_handler)

        if self.interval:
            file_handler = self._create_timed_rotating_file_handler()
        else:
            file_handler = self._create_file_handler()
        logger.addHandler(file_handler)

        return logger

    def _create_file_handler(self) -> logging.FileHandler:
        """
        Creates a logging FileHandler with the specified log file and level.

        Returns:
            logging.FileHandler: The file handler object.

        """
        handler = logging.FileHandler(
            filename=self.log_file,
            encoding="utf-8",
            mode="a",
        )
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            self._format_builder(),
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(self.file_log_level)
        return handler

    def _create_stream_handler(self) -> logging.StreamHandler:
        """
        Creates a logging StreamHandler with the specified log level.

        Returns:
            logging.StreamHandler: The created StreamHandler object.

        """
        handler = logging.StreamHandler()
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            self._format_builder(),
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(self.stream_log_level)
        return handler

    def _create_timed_rotating_file_handler(self) -> TimedRotatingFileHandler:
        """
        Creates a logging TimedRotatingFileHandler with the specified log file, level, interval, and backup count.

        Returns:
            logging.handlers.TimedRotatingFileHandler: The created TimedRotatingFileHandler object.
        """
        handler = TimedRotatingFileHandler(
            filename=self.log_file,
            when=self.interval,
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name}: {message}",
            datefmt=date_format,
            style="{",
        )
        handler.setFormatter(formatter)
        handler.setLevel(self.file_log_level)
        return handler

    def _format_builder(self) -> str:
        """
        Builds the format string for the logger.

        Returns:
            str: The format string for the logger.
        """
        format_string = ""
        if self.include_timestamp:
            format_string += "[{asctime}] "
        format_string += (
            "[{levelname:<" + str(self.log_level_left_padding) + "}] {name}: {message}"
        )
        return format_string

    def create_log_dir(self):
        """
        Creates a log directory if it does not exist.

        Args:
            log_dir (str): The path to the log directory.

        """
        os.makedirs(str(Path(self.log_file).parent), exist_ok=True)
