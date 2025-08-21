import sys
from pathlib import Path

from loguru import logger

logger.remove()

logger.add(
    sys.stderr,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="INFO",
)


def setup_file_logging(
    log_file: str = "logs/app.log",
    rotation: str = "10 MB",
    retention: str = "30 days",
    level: str = "DEBUG",
):
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_file,
        rotation=rotation,
        retention=retention,
        level=level,
        format=(
            "{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | "
            "{name}:{function}:{line} - {message}"
        ),
        backtrace=True,
        diagnose=True,
    )
