from prophet import Prophet
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def forecast_membership(df: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
    """Forecast membership using Prophet.
    
    Args:
        df: DataFrame with 'Date' and 'Membership_Count' columns
        periods: Number of months to forecast
        
    Returns:
        DataFrame with 'ds', 'yhat', 'yhat_lower', 'yhat_upper' columns
    """
    
    # Validate required columns
    required_cols = ['Date', 'Membership_Count']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    membership_df = df[['Date', 'Membership_Count']].dropna()
    if membership_df.empty:
        raise ValueError("No valid data for membership forecast after dropping NaN values")
    
    membership_df = membership_df.copy()
    membership_df.columns = ['ds', 'y']
    
    model = Prophet(yearly_seasonality=True, daily_seasonality=False)
    model.fit(membership_df)
    future = model.make_future_dataframe(periods=periods, freq='MS')
    forecast = model.predict(future)
    
    # Return only relevant columns
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

def forecast_call_volume(membership_forecast: pd.DataFrame, contact_rate: float) -> pd.DataFrame:
    """Calculate monthly call volume based on membership forecast and contact rate.
    
    Args:
        membership_forecast: DataFrame with 'yhat' column (annual membership)
        contact_rate: Annual contact rate (0-1)
        
    Returns:
        DataFrame with 'Monthly_Call_Volume' column added
    """
    if contact_rate < 0 or contact_rate > 1:
        logger.warning(f"Contact rate {contact_rate} is outside 0-1 range")
    
    membership_forecast = membership_forecast.copy()
    membership_forecast['Monthly_Call_Volume'] = (membership_forecast['yhat'] * contact_rate) / 12
    
    return membership_forecast