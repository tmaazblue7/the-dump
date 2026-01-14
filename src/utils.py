
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
def setup_logging(log_level: str = "INFO", log_file: str = None):
    """
    Configure logging for the project.
    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR).
        log_file (str): Optional path to log file.
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(asctime)s - %(levelname)s - %(message)s",
        filename=log_file if log_file else None
    )
    logging.info("Logging initialized.")

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
