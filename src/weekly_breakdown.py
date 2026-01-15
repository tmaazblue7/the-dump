import pandas as pd

from typing import List

def _get_month_weights(weekly_pattern: "pd.DataFrame | pd.Series", month_num: int) -> List[float]:
    """
    Return a normalized list of 4 weekly weights for the given month.
    Works with MultiIndex or simple Index. Falls back to equal weights.
    """
    import pandas as pd  # local import keeps function portable
    # Which months exist?
    if isinstance(weekly_pattern.index, pd.MultiIndex):
        months_in_index = weekly_pattern.index.get_level_values(0).unique()
    else:
        months_in_index = weekly_pattern.index.unique()

    if month_num in months_in_index:
        try:
            row = weekly_pattern.loc[month_num]
        except Exception:
            return [0.25, 0.25, 0.25, 0.25]
        if isinstance(row, pd.DataFrame):
            vals = row.squeeze().to_numpy().tolist()
        elif isinstance(row, pd.Series):
            vals = row.to_numpy().tolist()
        else:
            try:
                vals = list(row)
            except Exception:
                return [0.25, 0.25, 0.25, 0.25]
    else:
        return [0.25, 0.25, 0.25, 0.25]

    # Coerce to exactly 4 weights (merge overflow, pad short)
    if len(vals) > 4:
        vals = vals[:3] + [sum(vals[3:])]
    elif len(vals) < 4:
        vals = vals + [0.0] * (4 - len(vals))

    # Normalize safely
    total = sum(v for v in vals if pd.notna(v))
    if not total or total <= 0:
        return [0.25, 0.25, 0.25, 0.25]
    return [float(v)/float(total) if pd.notna(v) else 0.0 for v in vals]
def apply_weekly_seasonality(monthly_forecast, historical_df):
    historical_df['Historical_Call_Volume'] = pd.to_numeric(historical_df['Historical_Call_Volume'], errors='coerce')
    historical_df = historical_df.dropna(subset=['Historical_Call_Volume']).copy()

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
        weights = _get_month_weights(weekly_pattern, month_num)
        for i, weight in enumerate(weights):
            weekly_forecast.append({
                'Week_Start': month_start + pd.Timedelta(days=i * 7),
                'Estimated_Weekly_Call_Volume': row['Monthly_Call_Volume'] * weight,
                'Monthly_Call_Volume': row['Monthly_Call_Volume'],
                'Weight': weight,
                'Confidence_Interval_Lower': row['Monthly_Call_Volume'] * weight * 0.95,
                'Confidence_Interval_Upper': row['Monthly_Call_Volume'] * weight * 1.05
            })
    return pd.DataFrame(weekly_forecast)
