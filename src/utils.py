
import yaml
import logging
import pandas as pd

# -------------------------------
# 1. Load Configuration
# -------------------------------
def load_config(config_path: str):
    """
    Load configuration from a YAML file.
    Args:
        config_path (str): Path to the config.yaml file.
    Returns:
        dict: Parsed configuration dictionary.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            logging.info(f"Configuration loaded from {config_path}")
            return config
    except FileNotFoundError:
        logging.error(f"Config file not found at {config_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        raise

# -------------------------------
# 2. Logging Setup
# -------------------------------
from __future__ import annotations

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler  # optional if you want rotation

def setup_logging(log_level: str = "INFO", log_file: str | None = None, rotate: bool = False) -> None:
    """
    Configure logging to stdout and optionally to a file.
    - Creates the log directory if it doesn't exist.
    - Resolves relative paths relative to the repo root (…/the-dump/).
    - Supports optional log rotation.
    """
    # Level
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Always log to stdout
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]

    # If a log file is requested, resolve and ensure directory exists
    if log_file:
        # utils.py is in src/, so repo root is parents[1]
        repo_root = Path(__file__).resolve().parents[1]
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_path = repo_root / log_path

        # Ensure the directory exists
        log_path.parent.mkdir(parents=True, exist_ok=True)

        if rotate:
            file_handler = RotatingFileHandler(
                log_path, maxBytes=2_000_000, backupCount=5, encoding="utf-8"
            )
        else:
            file_handler = logging.FileHandler(log_path, encoding="utf-8")

        handlers.append(file_handler)

    # Use `handlers` rather than `filename` so we can add stdout + file
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=handlers,
        force=True,  # overwrite any prior basicConfig calls (Python 3.12 supports this)
    )

# -------------------------------
# 3. Save DataFrame to CSV
# -------------------------------
def save_dataframe(df: pd.DataFrame, file_path: str):
    """
    Save a DataFrame to CSV.
    Args:
        df (pd.DataFrame): DataFrame to save.
        file_path (str): Destination file path.
    """
    try:
        df.to_csv(file_path, index=False)
        logging.info(f"Data saved successfully to {file_path}")
    except Exception as e:
        logging.error(f"Error saving file {file_path}: {e}")
        raise

# -------------------------------
# 4. Validate Columns
# -------------------------------
def validate_columns(df: pd.DataFrame, required_cols: list):
    """
    Validate that required columns exist in the DataFrame.
    Args:
        df (pd.DataFrame): DataFrame to check.
        required_cols (list): List of required column names.
    Raises:
        ValueError: If any required column is missing.
    """
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        logging.error(f"Missing columns: {missing}")
        raise ValueError(f"Missing columns: {missing}")
    logging.info("All required columns are present.")

# -------------------------------
# 5. Parse Dates
# -------------------------------
def parse_dates(df: pd.DataFrame, date_col: str):
    """
    Convert a column to datetime format.
    Args:
        df (pd.DataFrame): DataFrame containing the date column.
        date_col (str): Name of the date column.
    Returns:
        pd.DataFrame: DataFrame with parsed date column.
    """
    try:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        logging.info(f"Date column '{date_col}' parsed successfully.")
        return df
    except Exception as e:
        logging.error(f"Error parsing date column '{date_col}': {e}")
        raise
