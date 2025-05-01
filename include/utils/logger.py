import logging


def get_logger(name: str) -> logging.Logger:
    """
    Initializes and returns a logger with INFO level logging.

    Args:
        name (str): Identifier for the logger.

    Returns:
        Logger: A logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
