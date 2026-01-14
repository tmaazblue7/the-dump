import streamlit as st
import plotly.express as px

def build_dashboard(monthly_forecast, weekly_forecast, contact_rate):
    """Streamlit dashboard for sensitivity analysis and visualization."""
    st.title("📊 Call Volume Forecast Dashboard")
    tab1, tab2, tab3 = st.tabs(["Overview", "Sensitivity Analysis", "Forecast Charts"])
    
    with tab1:
        st.subheader("Monthly Forecast")
        fig = px.line(monthly_forecast, x='ds', y='Monthly_Call_Volume', title='Monthly Call Volume Forecast')
        st.plotly_chart(fig)
    
    with tab2:
        st.subheader("Adjust Parameters")
        membership_input = st.slider("Membership Count", 150000, 200000, 170000)
        contact_rate_input = st.slider("Contact Rate", 0.3, 0.6, contact_rate)
        adjusted_weekly_volume = (membership_input * contact_rate_input / 12) / 4.345
        st.metric("Adjusted Weekly Call Volume", f"{adjusted_weekly_volume:,.0f}")
    
    with tab3:
        st.subheader("Weekly Breakdown")
        fig_weekly = px.line(weekly_forecast, x='Week_Start', y='Estimated_Weekly_Call_Volume', title='Weekly Call Volume Forecast')
        st.plotly_chart(fig_weekly)
