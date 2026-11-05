import atexit
import gzip
import shutil
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger


def _get_next_archive_name(log_dir: Path) -> str:
    """Get the base name for the next daily archive file (e.g. 19700101-1)."""

    today = datetime.now().strftime("%Y%m%d")
    log_dir.mkdir(parents=True, exist_ok=True)

    existing_archives = list(log_dir.glob(f"{today}-*.log.gz"))

    max_idx = 0
    for f in existing_archives:
        try:
            idx = int(f.name.split("-")[1].split(".")[0])
            max_idx = max(max_idx, idx)
        except (ValueError, IndexError):
            continue

    return f"{today}-{max_idx + 1}"


def _archive_latest_log(log_dir: Path):
    """Archive latest.log to a dated .gz file upon process exit."""

    latest_log = log_dir / "latest.log"
    if not latest_log.exists():
        return

    logger.complete()

    archive_base = _get_next_archive_name(log_dir)
    archive_path = log_dir / f"{archive_base}.log.gz"

    try:
        with gzip.open(archive_path, "wb") as f_out, open(latest_log, "rb") as f_in:
            shutil.copyfileobj(f_in, f_out)
    except Exception as e:
        print(f"[ERROR] Failed to archive log: {e}", file=sys.stderr)


def setup_logger(log_dir: Path, debug: bool = False) -> None:
    """Configure the logging system, handling latest.log and archiving automatically.

    :param log_dir: Directory to save the logs.
    :param debug: Whether to enable DEBUG level logs.
    """

    logger.remove()

    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    latest_log = log_dir / "latest.log"

    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}"

    logger.add(
        sys.stderr,
        format=console_format,
        level="DEBUG" if debug else "INFO",
        colorize=True,
    )

    logger.add(
        str(latest_log),
        format=file_format,
        level="DEBUG" if debug else "INFO",
        encoding="utf-8",
        enqueue=True,
        mode="w",
    )

    atexit.register(_archive_latest_log, log_dir)

    logger.info("[logger] Logger initialized")
