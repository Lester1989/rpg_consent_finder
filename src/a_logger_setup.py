import logging
import os

LOGGER_NAME = "content_consent_finder"


def setup_app_logging():
    """Configures logging for the application, leaving library loggers alone."""

    # Get the desired log level from the environment or use INFO as default
    log_level_str = os.getenv("LOGLEVEL", "DEBUG").upper()
    try:
        log_level = getattr(logging, log_level_str)
    except AttributeError:
        print(f"Invalid log level: {log_level_str}. Using INFO.")
        log_level = logging.INFO

    # Create a logger for your application
    app_logger = logging.getLogger(LOGGER_NAME)
    app_logger.setLevel(log_level)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)-8s - %(filename)+28s:%(lineno)3d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)

    # Add the handler to the application logger
    app_logger.addHandler(console_handler)

    return app_logger


setup_app_logging()
