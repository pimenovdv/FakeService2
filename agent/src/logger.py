import logging
import sys

def get_logger(name: str = "agent") -> logging.Logger:
    """
    Returns a configured logger for the agent application.
    """
    logger = logging.getLogger(name)

    # Only configure if the logger has no handlers to avoid duplicate logs
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        # Prevent the log messages from being duplicated in the root logger
        logger.propagate = False

    return logger
