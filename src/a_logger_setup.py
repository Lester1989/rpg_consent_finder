import logging

LOGGER_NAME = "content_consent_finder"
_LOGGER_CONFIGURED = False


def _create_console_handler(level: int) -> logging.Handler:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)-8s - %(filename)+28s:%(lineno)3d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    return handler


def configure_logging(log_level: str | int = "DEBUG") -> logging.Logger:
    """Configure and return the application logger."""

    global _LOGGER_CONFIGURED

    if isinstance(log_level, str):
        log_level = log_level.upper()
        log_level = getattr(logging, log_level, logging.INFO)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(log_level)

    if not _LOGGER_CONFIGURED:
        console_handler = _create_console_handler(log_level)
        logger.handlers.clear()
        logger.addHandler(console_handler)
        logger.propagate = False
        _LOGGER_CONFIGURED = True

    return logger
