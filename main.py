from src.data_preprocessing import load_and_merge_csv
from src.forecasting import forecast_membership, forecast_call_volume
from src.weekly_breakdown import apply_weekly_seasonality
from src.utils import load_config, setup_logging, save_dataframe
import pandas as pd
import os
from pathlib import Path

def main():
    # Initialize logging
    setup_logging(log_level="INFO", log_file="logs/project.log")

    # Load config
    config = load_config("config/config.yaml")

    # Example usage
    input_path = config['paths']['input_data']
    output_path = config['paths']['output_data']
    
    # Ensure output directory exists
    Path(output_path).mkdir(parents=True, exist_ok=True)

    # Load data
    df = load_and_merge_csv(input_path)
    lobs = df['LOB'].unique()

    monthly_results = []
    weekly_results = []

    for lob in lobs:
        lob_df = df[df['LOB'] == lob].copy()
        contact_rate = lob_df['Annual_Contact_Rate'].dropna().mean()
        
        # Use default contact rate if all values are NaN
        if pd.isna(contact_rate):
            contact_rate = config['contact_rate'].get('default', 0.45)

        # Membership Forecast
        membership_forecast = forecast_membership(
            lob_df,
            periods=config['forecast']['membership_periods'],
            fallback_on_insufficient=False,  # <-- fail hard
        )

        # Monthly call volume
        monthly_forecast = forecast_call_volume(membership_forecast[['ds', 'yhat']], contact_rate)
        monthly_forecast['LOB'] = lob
        monthly_forecast['Forecasted_Membership'] = monthly_forecast['yhat']
        monthly_forecast['lower_ci'] = monthly_forecast['Monthly_Call_Volume'] * 0.95
        monthly_forecast['upper_ci'] = monthly_forecast['Monthly_Call_Volume'] * 1.05
        monthly_forecast['Contact_Rate'] = contact_rate
        monthly_forecast['Model'] = 'Prophet'
        monthly_results.append(monthly_forecast)

        # Weekly breakdown
        weekly_forecast = apply_weekly_seasonality(monthly_forecast, lob_df)
        weekly_forecast['LOB'] = lob
        weekly_results.append(weekly_forecast)

    # Combine and save
    monthly_df = pd.concat(monthly_results, ignore_index=True)
    weekly_df = pd.concat(weekly_results, ignore_index=True)

    monthly_df.to_csv(f"{output_path}/{config['paths']['monthly_forecast_file']}", index=False)
    weekly_df.to_csv(f"{output_path}/{config['paths']['weekly_forecast_file']}", index=False)

    print("✅ Forecast files generated successfully!")

if __name__ == "__main__":
    main()