import streamlit as st
import plotly.express as px

def build_dashboard(monthly_forecast, weekly_forecast, contact_rate):
    """Streamlit dashboard for multi-LOB sensitivity analysis and visualization."""
    
    st.title("📊 Multi-LOB Call Volume Forecast Dashboard")
    
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
        contact_rate_input = st.slider("Contact Rate", 0.3, 0.6, contact_rate)
        
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