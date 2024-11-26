import os

from loguru import logger
from rich import print

from isra.src.config.constants import get_app_dir


class CustomLogger:
    """TODO: This custom logger is used to print to sysout using Rich (usually the output of the CLI tool)
    and to a file using Loguru's logger (for trazability purposes)"""

    def __init__(self, log_file: str):
        properties_dir = get_app_dir()
        self.log_file = os.path.join(properties_dir, log_file)
        logger.remove()
        logger.add(self.log_file, format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}", mode="w")
        logger.level("INFO")

    def iprint(self, message):
        """Prints a message to console output using the Rich print function"""
        print(message)

    def info(self, message):
        """Prints a message to log file using Loguru"""
        logger.info(message)

    def info2(self, message):
        """Prints a message to console output using the Rich print function and to a log file using loguru at the same
        time"""
        print(message)
        logger.info(message)

    def warning(self, message):
        logger.warning(message)

    def error(self, message):
        logger.error(message)

    def critical(self, message):
        logger.critical(message)

    def reset(self):
        open(self.log_file, "w").close()


logg = CustomLogger("component.log")
