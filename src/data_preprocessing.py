import pandas as pd
import glob

def load_and_merge_csv(input_path: str) -> pd.DataFrame:
    """Load and merge multiple CSV files into a single DataFrame."""
    files = glob.glob(f"{input_path}/*.csv")
    if not files:
        raise FileNotFoundError("No CSV files found in the specified directory.")
    df_list = [pd.read_csv(f) for f in files]
    merged_df = pd.concat(df_list, ignore_index=True)
    merged_df['Date'] = pd.to_datetime(merged_df['Date'])
    merged_df.sort_values('Date', inplace=True)
    return merged_df