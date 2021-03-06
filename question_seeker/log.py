import logging


LOGGER = logging.getLogger(__name__)


def set_log_config(
        filename: str = 'qs.log',
        level: str = 'info',
) -> logging.Logger:
    """
    Sets the configuration for logger

    Args:
        filename: str, name for logfile
        level: logger level

    Returns:
        Logger object
    """
    global LOGGER
    level = level.lower()
    level_lookup = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
    }
    logging.basicConfig(
        filename=filename,
        level=level_lookup[level],
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    )
    LOGGER = logging.getLogger(__name__)
    return LOGGER
