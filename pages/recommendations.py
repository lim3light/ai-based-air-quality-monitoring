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
    page_title="AirQual - Health Recommendations",
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
if 'current_aqi' not in st.session_state:
    st.session_state.current_aqi = None

# Check authentication
if not st.session_state.authenticated:
    st.warning("Please login to access health recommendations")
    st.stop()

# Get database connection
conn = database.get_connection()

# Sidebar
with st.sidebar:
    st.title("🌬️ AirQual")
    st.subheader("Health Recommendations")
    
    # Location selector
    st.subheader("Select Location")
    
    # Get user's saved locations
    user_data = database.get_user_data(conn, st.session_state.username)
    saved_locations = user_data.get('saved_locations', []) if user_data else []
    
    if saved_locations:
        locations = saved_locations.copy()
        
        # Ensure current location is in the list
        if st.session_state.location not in locations:
            locations.append(st.session_state.location)
            
        location = st.selectbox(
            "Choose from saved locations",
            options=locations,
            index=locations.index(st.session_state.location)
        )
    else:
        location = st.text_input("Enter location", value=st.session_state.location)
    
    if st.button("Set Location"):
        st.session_state.location = location
        st.rerun()
    
    # User health profile
    st.subheader("Your Health Profile")
    
    health_conditions = [
        "None/Healthy",
        "Asthma",
        "COPD",
        "Heart Disease",
        "Respiratory Allergies",
        "Elderly",
        "Pregnant",
        "Children",
        "Other"
    ]
    
    # Save health condition in session state if not already present
    if 'health_condition' not in st.session_state:
        st.session_state.health_condition = "None/Healthy"
    
    condition = st.selectbox(
        "Health Condition",
        options=health_conditions,
        index=health_conditions.index(st.session_state.health_condition)
    )
    
    if condition == "Other":
        custom_condition = st.text_input("Specify condition")
        if custom_condition:
            st.session_state.health_condition = custom_condition
    else:
        st.session_state.health_condition = condition
    
    # Additional health factors
    st.session_state.age_group = st.selectbox(
        "Age Group",
        options=["Child (0-12)", "Teen (13-18)", "Adult (19-60)", "Senior (60+)"],
        index=2  # Default to Adult
    )
    
    st.session_state.activity_level = st.selectbox(
        "Activity Level",
        options=["Sedentary", "Light Activity", "Moderate Activity", "Heavy Outdoor Activity"],
        index=1  # Default to Light Activity
    )

# Main content
st.title("Health Recommendations")
st.write(f"Based on air quality in **{st.session_state.location}**")

# Fetch current AQI data if not already available
if not st.session_state.current_aqi or st.session_state.current_aqi.get('location') != st.session_state.location:
    with st.spinner("Fetching air quality data..."):
        aqi_data = data.get_current_aqi(st.session_state.location)
        if aqi_data:
            st.session_state.current_aqi = aqi_data

# Display recommendations
if st.session_state.current_aqi:
    aqi_value = st.session_state.current_aqi.get('aqi', 0)
    aqi_category, aqi_color = utils.get_aqi_category(aqi_value)
    
    # Display AQI status
    st.markdown(
        f"<div style='background-color:{aqi_color};padding:20px;border-radius:10px;margin-bottom:20px;'>"
        f"<h2 style='text-align:center;color:white;'>Current AQI: {aqi_value} - {aqi_category}</h2>"
        "</div>",
        unsafe_allow_html=True
    )
    
    # Get detailed recommendations
    detailed_recs = get_recommendations(aqi_value, detailed=True)
    
    # General health advice
    st.subheader("General Health Advice")
    st.info(detailed_recs['general_detailed'])
    
    # Personalized recommendations
    st.subheader("Personalized Recommendations")
    
    # Based on health condition
    if st.session_state.health_condition != "None/Healthy":
        personalized_advice = utils.get_personalized_recommendation(aqi_value, st.session_state.health_condition)
        st.write(personalized_advice)
    
    # Tabs for different demographic groups
    st.subheader("Recommendations by Group")
    
    tabs = st.tabs(["General Population", "Sensitive Groups", "Children", "Elderly", "Outdoor Workers"])
    
    with tabs[0]:
        st.write(detailed_recs['general_population'])
        
    with tabs[1]:
        st.write(detailed_recs['sensitive_groups'])
        
    with tabs[2]:
        st.write(detailed_recs['children'])
        
    with tabs[3]:
        st.write(detailed_recs['elderly'])
        
    with tabs[4]:
        st.write(detailed_recs['outdoor_workers'])
    
    # Protection measures
    st.subheader("Protection Measures")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Indoor Protection:**")
        for item in detailed_recs['indoor_protection']:
            st.write(f"- {item}")
    
    with col2:
        st.write("**Outdoor Protection:**")
        for item in detailed_recs['outdoor_protection']:
            st.write(f"- {item}")
    
    # AQI impact explanation
    st.subheader("Health Impact Information")
    st.write(detailed_recs['health_impacts'])
    
    # Display pollutant-specific advice if available
    pollutants = st.session_state.current_aqi.get('pollutants', {})
    if pollutants:
        st.subheader("Pollutant-Specific Advice")
        
        # Create expandable sections for each pollutant
        if 'pm25' in pollutants or 'PM2.5' in pollutants:
            pm25_val = pollutants.get('pm25', pollutants.get('PM2.5', 0))
            with st.expander("PM2.5 - Fine Particulate Matter"):
                st.write(f"**Current level:** {pm25_val} μg/m³")
                
                if pm25_val <= 12:
                    st.write("**Health impact:** Minimal health risk. PM2.5 levels are good.")
                    st.write("**Recommendation:** No special precautions needed.")
                elif pm25_val <= 35:
                    st.write("**Health impact:** May cause respiratory symptoms in sensitive individuals with prolonged exposure.")
                    st.write("**Recommendation:** People with respiratory or heart conditions should limit prolonged outdoor exertion.")
                elif pm25_val <= 55:
                    st.write("**Health impact:** May cause increased respiratory symptoms in sensitive individuals.")
                    st.write("**Recommendation:** People with respiratory or heart conditions should avoid outdoor exertion.")
                else:
                    st.write("**Health impact:** May cause respiratory effects in the general population.")
                    st.write("**Recommendation:** Everyone should reduce or avoid outdoor exertion.")
        
        if 'pm10' in pollutants or 'PM10' in pollutants:
            pm10_val = pollutants.get('pm10', pollutants.get('PM10', 0))
            with st.expander("PM10 - Coarse Particulate Matter"):
                st.write(f"**Current level:** {pm10_val} μg/m³")
                
                if pm10_val <= 54:
                    st.write("**Health impact:** Minimal health risk. PM10 levels are good.")
                    st.write("**Recommendation:** No special precautions needed.")
                elif pm10_val <= 154:
                    st.write("**Health impact:** May cause respiratory irritation with prolonged exposure.")
                    st.write("**Recommendation:** Unusually sensitive people should consider reducing prolonged outdoor exertion.")
                elif pm10_val <= 254:
                    st.write("**Health impact:** May cause respiratory symptoms in sensitive groups.")
                    st.write("**Recommendation:** People with respiratory disease should limit outdoor exertion.")
                else:
                    st.write("**Health impact:** May cause respiratory effects in the general population.")
                    st.write("**Recommendation:** Everyone should reduce outdoor exertion.")
        
        if 'o3' in pollutants or 'O3' in pollutants:
            o3_val = pollutants.get('o3', pollutants.get('O3', 0))
            with st.expander("O3 - Ozone"):
                st.write(f"**Current level:** {o3_val} μg/m³")
                
                if o3_val <= 54:
                    st.write("**Health impact:** Minimal health risk. Ozone levels are good.")
                    st.write("**Recommendation:** No special precautions needed.")
                elif o3_val <= 124:
                    st.write("**Health impact:** May cause respiratory irritation during prolonged outdoor activity.")
                    st.write("**Recommendation:** Unusually sensitive people should consider limiting prolonged outdoor exertion.")
                else:
                    st.write("**Health impact:** May cause respiratory effects and breathing discomfort in sensitive groups and active people.")
                    st.write("**Recommendation:** People with respiratory conditions, children, and older adults should limit outdoor activity.")
    
    # Health monitoring section
    st.subheader("Daily Health Monitoring")
    
    st.write("Keep track of any symptoms you experience in relation to air quality:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Common symptoms to watch for:**")
        st.write("- Coughing or throat irritation")
        st.write("- Shortness of breath")
        st.write("- Wheezing")
        st.write("- Eye irritation")
        st.write("- Fatigue")
        st.write("- Chest discomfort")
    
    with col2:
        st.write("**When to seek medical attention:**")
        st.write("- Severe shortness of breath")
        st.write("- Chest pain")
        st.write("- Severe wheezing")
        st.write("- Symptoms that don't improve after taking medication")
        st.write("- Symptoms that worsen despite taking precautions")
    
    # Air quality forecast and planning
    st.subheader("Plan Your Week")
    
    # Try to predict trend for next few days
    trend_prediction = utils.predict_aqi_trend(
        database.get_historical_aqi(
            conn, 
            st.session_state.username, 
            st.session_state.location,
            datetime.now() - timedelta(days=30),
            datetime.now()
        )
    )
    
    if trend_prediction:
        st.write("Based on historical trends, here's a forecast of air quality for the next few days:")
        
        # Create forecast table
        forecast_df = pd.DataFrame(trend_prediction)
        forecast_df['category'] = forecast_df['aqi'].apply(lambda x: utils.get_aqi_category(x)[0])
        forecast_df['color'] = forecast_df['aqi'].apply(lambda x: utils.get_aqi_category(x)[1])
        
        # Format date
        forecast_df['date'] = pd.to_datetime(forecast_df['date']).dt.strftime('%a, %b %d')
        
        # Display forecast in columns
        cols = st.columns(len(forecast_df))
        
        for i, (_, row) in enumerate(forecast_df.iterrows()):
            with cols[i]:
                st.markdown(
                    f"""
                    <div style="background-color:{row['color']};padding:10px;border-radius:5px;text-align:center;">
                        <p style="color:white;margin:0;">{row['date']}</p>
                        <h3 style="color:white;margin:0;">{row['aqi']}</h3>
                        <p style="color:white;margin:0;">{row['category']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Activity planning advice
        st.write("**Activity Planning Advice:**")
        
        best_day = forecast_df.loc[forecast_df['aqi'].idxmin()]
        worst_day = forecast_df.loc[forecast_df['aqi'].idxmax()]
        
        st.write(f"- Best day for outdoor activities: **{best_day['date']}** (AQI: {best_day['aqi']})")
        st.write(f"- Day to take extra precautions: **{worst_day['date']}** (AQI: {worst_day['aqi']})")
        
        # Suggestion based on user's activity level
        if st.session_state.activity_level in ["Moderate Activity", "Heavy Outdoor Activity"]:
            best_days = forecast_df[forecast_df['aqi'] < 100]
            if not best_days.empty:
                best_days_str = ", ".join(best_days['date'])
                st.write(f"- Recommended days for {st.session_state.activity_level}: **{best_days_str}**")
            else:
                st.write(f"- Consider indoor alternatives for {st.session_state.activity_level} in the coming days.")
    else:
        st.info("Not enough historical data to provide a forecast. Continue using the dashboard to collect data for better predictions.")
    
    # Air quality improvement tips
    with st.expander("Tips to Improve Indoor Air Quality"):
        st.write("**1. Use air purifiers with HEPA filters**")
        st.write("**2. Keep windows closed when outdoor air quality is poor**")
        st.write("**3. Avoid activities that generate indoor pollutants:**")
        st.write("   - Smoking")
        st.write("   - Burning candles or incense")
        st.write("   - Using aerosol products")
        st.write("**4. Regularly clean and maintain your home:**")
        st.write("   - Vacuum with HEPA filter")
        st.write("   - Dust with damp cloth")
        st.write("   - Wash bedding weekly")
        st.write("**5. Control humidity levels (keep between 30-50%)**")
        st.write("**6. Ensure proper ventilation when cooking**")
    
    # Educational resources
    with st.expander("Learn More About Air Quality and Health"):
        st.write("**Recommended Resources:**")
        st.write("- [EPA: Air Quality and Health](https://www.epa.gov/air-research/air-quality-and-health)")
        st.write("- [WHO: Ambient Air Pollution](https://www.who.int/news-room/fact-sheets/detail/ambient-(outdoor)-air-quality-and-health)")
        st.write("- [CDC: Air Quality](https://www.cdc.gov/air/default.htm)")
        st.write("- [AirNow: Air Quality Information](https://www.airnow.gov/)")
        st.write("- [American Lung Association: Air Quality](https://www.lung.org/clean-air)")
    
else:
    st.error("Failed to fetch air quality data. Please check the location name or try again later.")

# Footer
st.markdown("---")
st.markdown("AirQual - AI Air Quality Monitoring System")
st.markdown("Data sources: OpenAQ and other air quality monitoring networks")
