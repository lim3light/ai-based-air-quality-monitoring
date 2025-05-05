import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import data
import utils
import database
from recommendations import get_recommendations

# Page configuration
st.set_page_config(
    page_title="AirQual - Dashboard",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state if needed
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'location' not in st.session_state:
    st.session_state.location = "London"  # Default location

# Check authentication
if not st.session_state.authenticated:
    st.warning("Please login to access the dashboard")
    st.stop()

# Get database connection
conn = database.get_connection()

# Sidebar for location selection
with st.sidebar:
    st.title("🌬️ AirQual")
    st.subheader("Dashboard")
    
    # Location selector
    st.subheader("Select Location")
    location_input = st.text_input("City name", value=st.session_state.location)
    search_button = st.button("Search")
    
    if search_button and location_input:
        try:
            st.session_state.location = location_input
            st.rerun()
        except Exception as e:
            st.error(f"Error setting location: {str(e)}")
    
    # Show saved locations
    if 'locations' in st.session_state and st.session_state.locations:
        st.subheader("Saved Locations")
        for loc in st.session_state.locations:
            if st.button(f"📍 {loc}", key=f"loc_{loc}"):
                st.session_state.location = loc
                st.rerun()
    
    # Date range for historical data
    st.subheader("Date Range")
    days_back = st.slider("Days to show", min_value=1, max_value=30, value=7)
    
    # Update frequency
    st.subheader("Update Settings")
    auto_refresh = st.checkbox("Auto refresh data", value=False)
    if auto_refresh:
        refresh_interval = st.slider("Refresh interval (minutes)", min_value=5, max_value=60, value=15)

# Main content
st.title(f"Air Quality Dashboard for {st.session_state.location}")

# Fetch current AQI data
with st.spinner("Fetching air quality data..."):
    aqi_data = data.get_current_aqi(st.session_state.location)

if aqi_data:
    # Store current AQI in session state
    st.session_state.current_aqi = aqi_data
    
    # Display current AQI in a prominent box
    aqi_value = aqi_data.get('aqi', 0)
    aqi_category, aqi_color = utils.get_aqi_category(aqi_value)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color:{aqi_color};padding:20px;border-radius:10px;text-align:center;">
                <h1 style="color:white;margin:0;">{aqi_value}</h1>
                <h3 style="color:white;margin:0;">AQI</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style="background-color:{aqi_color};padding:20px;border-radius:10px;">
                <h2 style="color:white;margin:0;">{aqi_category}</h2>
                <p style="color:white;margin:0;">Last updated: {utils.format_timestamp(aqi_data.get('timestamp', datetime.now().isoformat()))}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Row for quick stats and save location button
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        recommendations = get_recommendations(aqi_value)
        st.subheader("Quick Health Advice")
        st.info(recommendations['general'])
    
    with col2:
        st.subheader("Protection Measures")
        st.info(recommendations['protection'])
    
    with col3:
        st.subheader("Actions")
        # Save location button
        if 'locations' in st.session_state and st.session_state.location not in st.session_state.locations:
            if st.button("📌 Save Location"):
                st.session_state.locations.append(st.session_state.location)
                database.update_user_locations(conn, st.session_state.username, st.session_state.locations)
                st.success(f"{st.session_state.location} saved to your locations")
                st.rerun()
        else:
            if st.button("❌ Remove Location"):
                st.session_state.locations.remove(st.session_state.location)
                database.update_user_locations(conn, st.session_state.username, st.session_state.locations)
                st.success(f"{st.session_state.location} removed from your locations")
                st.rerun()
    
    # Display pollutants data
    st.subheader("Pollutant Levels")
    
    pollutants = aqi_data.get('pollutants', {})
    if pollutants:
        # Format pollutant names and values
        formatted_pollutants = {}
        for key, value in pollutants.items():
            # Clean up pollutant name
            if key.lower() == 'pm25':
                display_name = 'PM2.5'
            elif key.lower() == 'pm10':
                display_name = 'PM10'
            else:
                display_name = key.upper()
            
            formatted_pollutants[display_name] = value
        
        # Create columns for each pollutant
        cols = st.columns(len(formatted_pollutants))
        
        for i, (pollutant, value) in enumerate(formatted_pollutants.items()):
            with cols[i]:
                # Determine color based on pollutant level
                # This is a simplified approach - real thresholds would be pollutant-specific
                if pollutant == 'PM2.5':
                    if value <= 12:
                        color = '#4CAF50'  # Green
                    elif value <= 35.4:
                        color = '#FFEB3B'  # Yellow
                    elif value <= 55.4:
                        color = '#FF9800'  # Orange
                    else:
                        color = '#F44336'  # Red
                elif pollutant == 'PM10':
                    if value <= 54:
                        color = '#4CAF50'  # Green
                    elif value <= 154:
                        color = '#FFEB3B'  # Yellow
                    elif value <= 254:
                        color = '#FF9800'  # Orange
                    else:
                        color = '#F44336'  # Red
                else:
                    # Generic coloring for other pollutants
                    if value <= 50:
                        color = '#4CAF50'  # Green
                    elif value <= 100:
                        color = '#FFEB3B'  # Yellow
                    elif value <= 150:
                        color = '#FF9800'  # Orange
                    else:
                        color = '#F44336'  # Red
                
                st.markdown(
                    f"""
                    <div style="background-color:{color};padding:10px;border-radius:5px;text-align:center;">
                        <h4 style="color:white;margin:0;">{pollutant}</h4>
                        <h2 style="color:white;margin:0;">{value}</h2>
                        <p style="color:white;margin:0;">μg/m³</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("Detailed pollutant data not available for this location")
    
    # Historical data trend
    st.subheader("Historical AQI Trend")
    
    # Fetch historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    historical_data = database.get_historical_aqi(
        conn, 
        st.session_state.username, 
        st.session_state.location,
        start_date,
        end_date
    )
    
    if historical_data:
        # Convert to DataFrame for plotting
        df = pd.DataFrame(historical_data)
        
        # Ensure datetime format
        if 'timestamp' in df.columns and df['timestamp'].dtype != 'datetime64[ns]':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create line chart
        fig = px.line(
            df, 
            x='timestamp', 
            y='aqi', 
            title=f"AQI Trend for {st.session_state.location} (Last {days_back} Days)",
            labels={'timestamp': 'Date', 'aqi': 'AQI Value'},
            markers=True
        )
        
        # Add color zones for AQI categories
        fig.add_hrect(y0=0, y1=50, line_width=0, fillcolor="green", opacity=0.1)
        fig.add_hrect(y0=50, y1=100, line_width=0, fillcolor="yellow", opacity=0.1)
        fig.add_hrect(y0=100, y1=150, line_width=0, fillcolor="orange", opacity=0.1)
        fig.add_hrect(y0=150, y1=200, line_width=0, fillcolor="red", opacity=0.1)
        fig.add_hrect(y0=200, y1=300, line_width=0, fillcolor="purple", opacity=0.1)
        fig.add_hrect(y0=300, y1=500, line_width=0, fillcolor="maroon", opacity=0.1)
        
        # Add text annotations for categories
        fig.add_annotation(x=df['timestamp'].min(), y=25, text="Good", showarrow=False, xanchor="left")
        fig.add_annotation(x=df['timestamp'].min(), y=75, text="Moderate", showarrow=False, xanchor="left")
        fig.add_annotation(x=df['timestamp'].min(), y=125, text="Unhealthy for Sensitive Groups", showarrow=False, xanchor="left")
        fig.add_annotation(x=df['timestamp'].min(), y=175, text="Unhealthy", showarrow=False, xanchor="left")
        fig.add_annotation(x=df['timestamp'].min(), y=250, text="Very Unhealthy", showarrow=False, xanchor="left")
        fig.add_annotation(x=df['timestamp'].min(), y=400, text="Hazardous", showarrow=False, xanchor="left")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistics row
        st.subheader("Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average AQI", round(df['aqi'].mean(), 1))
        
        with col2:
            st.metric("Maximum AQI", df['aqi'].max())
        
        with col3:
            st.metric("Minimum AQI", df['aqi'].min())
        
        with col4:
            # Calculate AQI trend (improving or worsening)
            if len(df) >= 2:
                latest_aqi = df['aqi'].iloc[-1]
                previous_aqi = df['aqi'].iloc[-2]
                delta = latest_aqi - previous_aqi
                delta_label = f"{abs(delta):.1f}"
                
                st.metric(
                    "AQI Trend", 
                    f"{latest_aqi:.1f}", 
                    delta=delta_label if delta != 0 else "0",
                    delta_color="inverse"  # Lower is better for AQI
                )
            else:
                st.metric("Latest AQI", df['aqi'].iloc[-1])
    else:
        st.info(f"No historical data available for {st.session_state.location}. Visit this dashboard regularly to build up historical data.")
    
    # Save AQI data to database for history
    database.save_aqi_reading(conn, st.session_state.username, st.session_state.location, aqi_value, aqi_data)
    
    # Auto-refresh logic
    if auto_refresh:
        st.markdown(f"<p>Dashboard will refresh in {refresh_interval} minutes</p>", unsafe_allow_html=True)
        st.markdown("""
        <script>
            setTimeout(function() {
                window.location.reload();
            }, %s);
        </script>
        """ % (refresh_interval * 60 * 1000), unsafe_allow_html=True)

else:
    st.error("Failed to fetch air quality data. Please check the location name or try again later.")
