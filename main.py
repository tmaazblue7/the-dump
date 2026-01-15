
from prophet import Prophet
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def forecast_membership(
    df: pd.DataFrame,
    periods: int = 12,
    date_col: str = "Date",
    value_col: str = "Membership_Count",
    fallback_on_insufficient: bool = True,
) -> pd.DataFrame:
    """
    Forecast membership as a monthly stock series using Prophet.

    - Cleans date/value columns
    - Aggregates to month-end (last value in month)
    - Validates at least 2 observations before fitting
    - Uses MonthEnd offsets (version-proof vs 'M'/'ME' alias differences)
    """
    # 1) Validate schema
    missing = [c for c in (date_col, value_col) if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data = df[[date_col, value_col]].copy()

    # 2) Coerce numeric Membership_Count (strip non-numeric if needed)
    if data[value_col].dtype == object:
        data[value_col] = (
            data[value_col]
            .astype(str)
            .str.replace(r"[^0-9+\\-\\.]", "", regex=True)
        )
    data[value_col] = pd.to_numeric(data[value_col], errors="coerce")

    # 3) Parse dates
    data[date_col] = pd.to_datetime(data[date_col], errors="coerce")

    # 4) Drop invalid
    data = data.dropna(subset=[date_col, value_col]).copy()
    if data.empty:
        raise ValueError("No valid data for membership forecast after cleaning.")

    # 5) Aggregate to month-end last (unique ds)
    me = pd.offsets.MonthEnd(1)
    monthly = (
        data.sort_values(date_col)
            .set_index(date_col)[[value_col]]
            .resample(me).last()
            .dropna()
            .rename(columns={value_col: "y"})
    )
    monthly.index.name = "ds"
    history = monthly.reset_index()[["ds", "y"]]

    # 6) Validate length
    if len(history) < 2:
        msg = f"Insufficient membership history after monthly aggregation: {len(history)} rows."
        if fallback_on_insufficient:
            logger.warning("%s Returning a naive flat forecast.", msg)
            last_ds = history["ds"].max() if len(history) else pd.Timestamp.today().normalize()
            last_y = float(history["y"].iloc[-1]) if len(history) else 0.0
            future_ds = pd.date_range(last_ds, periods=periods, freq=me, inclusive="right")
            out = pd.DataFrame({
                "ds": future_ds,
                "yhat": [last_y] * periods,
                "yhat_lower": [last_y] * periods,
                "yhat_upper": [last_y] * periods,
            })
            return out
        else:
            raise ValueError(msg)

    # 7) Fit Prophet (monthly → no weekly/daily; cap changepoints for short series)
    n_cp = max(0, min(10, len(history) - 2))
    m = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        n_changepoints=n_cp,
        growth="linear",
    )
    # Quiet libraries if desired
    logging.getLogger("prophet").setLevel(logging.WARNING)
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

    m.fit(history)
    future = m.make_future_dataframe(periods=periods, freq=me, include_history=False)
    forecast = m.predict(future)
    return forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].copy()