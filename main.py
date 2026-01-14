from src.data_preprocessing import load_and_merge_csv
from src.forecasting import forecast_membership, forecast_call_volume
from src.weekly_breakdown import apply_weekly_seasonality
from src.validation import validate_forecast
from src.ui import build_dashboard
import streamlit as st

def main():
    # Load data
    df = load_and_merge_csv("data/data_inputs")
    
    # Forecast membership
    membership_forecast = forecast_membership(df)
    
    # Forecast call volume
    contact_rate = df['Annual_Contact_Rate'].dropna().mean()
    monthly_forecast = forecast_call_volume(membership_forecast[['ds', 'yhat']], contact_rate)
    
    # Weekly breakdown
    weekly_forecast = apply_weekly_seasonality(monthly_forecast, df)
    
    # Validate
    actual = df['Historical_Call_Volume'].dropna()
    predicted = df['Membership_Count'].dropna() * contact_rate / 12
    metrics = validate_forecast(actual, predicted)
    print(metrics)
    
    # Streamlit UI
    build_dashboard(monthly_forecast, weekly_forecast, contact_rate)
    
    # Sidebar LOB selection
    lob_options = df['LOB'].unique()
    selected_lob = st.sidebar.selectbox("Select Line of Business (LOB):", lob_options)

    # Filter forecasts by LOB
    lob_monthly_forecast = monthly_forecast[monthly_forecast['LOB'] == selected_lob]
    lob_weekly_forecast = weekly_forecast[weekly_forecast['LOB'] == selected_lob]

    # Display charts for selected LOB
    st.subheader(f"Forecast for {selected_lob}")
    fig_monthly = px.line(lob_monthly_forecast, x='ds', y='Monthly_Call_Volume', title=f'Monthly Forecast - {selected_lob}')
    st.plotly_chart(fig_monthly)

    fig_weekly = px.line(lob_weekly_forecast, x='Week_Start', y='Estimated_Weekly_Call_Volume', title=f'Weekly Forecast - {selected_lob}')
    st.plotly_chart(fig_weekly)


if __name__ == "__main__":
    main()