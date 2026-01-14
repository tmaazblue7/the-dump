import streamlit as st
import pandas as pd
import plotly.express as px

# Paths to output files
MONTHLY_FILE = "data/data_outputs/monthly_forecast.csv"
WEEKLY_FILE = "data/data_outputs/weekly_forecast.csv"

def load_forecast_data():
    """Load monthly and weekly forecast data from CSV files."""
    monthly_df = pd.read_csv(MONTHLY_FILE)
    weekly_df = pd.read_csv(WEEKLY_FILE)
    
    # Ensure date columns are parsed correctly
    monthly_df['ds'] = pd.to_datetime(monthly_df['ds'])
    weekly_df['Week_Start'] = pd.to_datetime(weekly_df['Week_Start'])
    
    return monthly_df, weekly_df

def build_dashboard():
    st.title("📊 Multi-LOB Call Volume Forecast Dashboard")
    
    # Load data
    monthly_forecast, weekly_forecast = load_forecast_data()
    
    # Sidebar: LOB selection
    lob_options = monthly_forecast['LOB'].unique()
    selected_lobs = st.sidebar.multiselect("Select Line(s) of Business:", lob_options, default=lob_options[:1])
    
    # Filter data by selected LOB(s)
    lob_monthly = monthly_forecast[monthly_forecast['LOB'].isin(selected_lobs)]
    lob_weekly = weekly_forecast[weekly_forecast['LOB'].isin(selected_lobs)]
    
    # Tabs for navigation
    tab1, tab2, tab3 = st.tabs(["Overview", "Sensitivity Analysis", "Forecast Charts"])
    
    # ---- Tab 1: Overview ----
    with tab1:
        st.subheader("Monthly Forecast by LOB")
        fig_monthly = px.line(
            lob_monthly,
            x='ds',
            y='Monthly_Call_Volume',
            color='LOB',
            title='Monthly Call Volume Forecast by LOB'
        )
        st.plotly_chart(fig_monthly, use_container_width=True)
        
        st.subheader("Weekly Forecast by LOB")
        fig_weekly = px.line(
            lob_weekly,
            x='Week_Start',
            y='Estimated_Weekly_Call_Volume',
            color='LOB',
            title='Weekly Call Volume Forecast by LOB'
        )
        st.plotly_chart(fig_weekly, use_container_width=True)
    
    # ---- Tab 2: Sensitivity Analysis ----
    with tab2:
        st.subheader("Adjust Parameters for Sensitivity Analysis")
        membership_input = st.slider("Membership Count", 150000, 200000, 170000)
        contact_rate_input = st.slider("Contact Rate", 0.3, 0.6, 0.45)
        
        adjusted_weekly_volume = (membership_input * contact_rate_input / 12) / 4.345
        st.metric("Adjusted Weekly Call Volume (per LOB)", f"{adjusted_weekly_volume:,.0f}")
        
        st.write("Impact on Weekly Forecast for Selected LOB(s):")
        fig_adjusted = px.line(
            lob_weekly,
            x='Week_Start',
            y='Estimated_Weekly_Call_Volume',
            color='LOB',
            title='Adjusted Weekly Forecast by LOB'
        )
        st.plotly_chart(fig_adjusted, use_container_width=True)
    
    # ---- Tab 3: Forecast Charts ----
    with tab3:
        st.subheader("Confidence Interval Visualization")
        fig_ci = px.area(
            lob_monthly,
            x='ds',
            y='Monthly_Call_Volume',
            color='LOB',
            title='Confidence Intervals by LOB',
            facet_col='LOB'
        )
        st.plotly_chart(fig_ci, use_container_width=True)

# Run the dashboard
if __name__ == "__main__":
    build_dashboard()
