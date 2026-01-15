
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO",
                  log_file: str | None = "logs/project.log",
                  rotate: bool = False) -> None:
    """
    Configure logging to stdout and (optionally) to a file.
    - Ensures the log directory exists to avoid FileNotFoundError.
    - Resolves relative file paths to the repository root (…/the-dump/).
    - Optionally enables log rotation.
    """
    # Determine level (fallback to INFO if invalid)
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create a consistent formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s"
    )

    # Always log to stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(level)
    stdout_handler.setFormatter(formatter)
    handlers: list[logging.Handler] = [stdout_handler]

    # If a log file is requested, resolve and ensure directory exists
    if log_file:
        # utils.py is in src/, so repo root is parents[1]
        repo_root = Path(__file__).resolve().parents[1]
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = repo_root / log_path
        # Ensure logs/ exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if rotate:
            file_handler = RotatingFileHandler(
                log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
            )
        else:
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    # Configure root logger with our handlers; force=True replaces prior config
    logging.basicConfig(level=level, handlers=handlers, force=True)
