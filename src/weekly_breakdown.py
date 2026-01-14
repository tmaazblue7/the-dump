import pandas as pd

def apply_weekly_seasonality(monthly_forecast: pd.DataFrame, historical_df: pd.DataFrame) -> pd.DataFrame:
    """Distribute monthly call volume into weeks using seasonality-adjusted weights."""
    # Compute weights from historical data
    historical_df['Month'] = historical_df['Date'].dt.month
    historical_df['Week'] = historical_df['Date'].dt.isocalendar().week
    weekly_pattern = (
        historical_df.groupby(['Month', 'Week'])['Historical_Call_Volume']
        .sum()
        .groupby(level=0)
        .apply(lambda x: x / x.sum())
    )
    weekly_forecast = []
    for _, row in monthly_forecast.iterrows():
        month_start = pd.to_datetime(row['ds'])
        month_num = month_start.month
        weights = weekly_pattern.loc[month_num] if month_num in weekly_pattern.index.levels[0] else [0.25, 0.25, 0.25, 0.25]
        for i, weight in enumerate(weights):
            weekly_forecast.append({
                'Week_Start': month_start + pd.Timedelta(days=i * 7),
                'Estimated_Weekly_Call_Volume': row['Monthly_Call_Volume'] * weight
            })
    return pd.DataFrame(weekly_forecast)