from prophet import Prophet
import pandas as pd

def forecast_membership(df: pd.DataFrame, periods: int = 12) -> pd.DataFrame:
    """Forecast membership using Prophet."""
    membership_df = df[['Date', 'Membership_Count']].dropna()
    membership_df.columns = ['ds', 'y']
    model = Prophet(yearly_seasonality=True)
    model.fit(membership_df)
    future = model.make_future_dataframe(periods=periods, freq='ME')
    forecast = model.predict(future)
    return forecast

def forecast_call_volume(membership_forecast: pd.DataFrame, contact_rate: float) -> pd.DataFrame:
    """Calculate monthly call volume based on membership forecast and contact rate."""
    membership_forecast = membership_forecast.copy()
    membership_forecast['Monthly_Call_Volume'] = membership_forecast['yhat'] * contact_rate / 12
    return membership_forecast