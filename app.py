import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
import os

import auth
import data
import utils
import database
from recommendations import get_recommendations

# Page configuration
st.set_page_config(
    page_title="AirQual - AI Air Quality Monitor",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'location' not in st.session_state:
    st.session_state.location = "London"  # Default location
if 'locations' not in st.session_state:
    st.session_state.locations = []
if 'current_aqi' not in st.session_state:
    st.session_state.current_aqi = None

# Database connection
conn = database.get_connection()

# Authentication sidebar
with st.sidebar:
    st.title("🌬️ AirQual")
    st.subheader("AI Air Quality Monitor")
    
    if not st.session_state.authenticated:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login"):
                if auth.verify_user(conn, username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    user_data = database.get_user_data(conn, username)
                    if user_data and 'saved_locations' in user_data:
                        st.session_state.locations = user_data['saved_locations']
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with tab2:
            st.subheader("Register")
            new_username = st.text_input("Choose Username", key="reg_username")
            new_password = st.text_input("Choose Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            
            if st.button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif auth.register_user(conn, new_username, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username already exists or registration failed")
    else:
        st.success(f"Logged in as {st.session_state.username}")
        
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
        if st.session_state.locations:
            st.subheader("Saved Locations")
            for loc in st.session_state.locations:
                if st.button(f"📍 {loc}", key=f"loc_{loc}"):
                    st.session_state.location = loc
                    st.rerun()
        
        # Logout button
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

# Main content
if not st.session_state.authenticated:
    st.title("Welcome to AirQual")
    st.write("Please login or register to access the air quality monitoring dashboard.")
    
    # Sample dashboard preview
    st.subheader("Preview of our Air Quality Dashboard")
    col1, col2 = st.columns(2)
    
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/4107/4107793.png", width=150)
        st.write("Real-time air quality monitoring from anywhere in the world")
        
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/1186/1186330.png", width=150)
        st.write("Personalized health recommendations based on air quality")
    
    st.subheader("Features")
    features = [
        "🌐 Real-time AQI monitoring",
        "📊 Interactive data visualization",
        "📱 Mobile responsive design",
        "🔔 Health alerts and recommendations",
        "📍 Multiple location tracking",
        "📈 Historical data analysis",
        "🧠 AI-powered health insights"
    ]
    
    for feature in features:
        st.write(feature)

else:
    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(["Current AQI", "History", "Profile", "Health Recommendations"])
    
    with tab1:
        st.title(f"Air Quality in {st.session_state.location}")
        
        # Fetch current AQI data
        with st.spinner("Fetching air quality data..."):
            aqi_data = data.get_current_aqi(st.session_state.location)
            
        if aqi_data and 'error' not in aqi_data:
            st.session_state.current_aqi = aqi_data
            
            # Display AQI with color indicator
            aqi_value = aqi_data.get('aqi', 0)
            aqi_category, aqi_color = utils.get_aqi_category(aqi_value)
            
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                st.metric("Current AQI", value=aqi_value)
            
            with col2:
                st.markdown(
                    f"<div style='background-color:{aqi_color};padding:10px;border-radius:5px;'>"
                    f"<h2 style='text-align:center;color:white;'>{aqi_category}</h2>"
                    "</div>",
                    unsafe_allow_html=True
                )
            
            with col3:
                # Save location button
                if st.session_state.location not in st.session_state.locations:
                    if st.button("Save Location"):
                        st.session_state.locations.append(st.session_state.location)
                        database.update_user_locations(conn, st.session_state.username, st.session_state.locations)
                        st.success(f"{st.session_state.location} saved to your locations")
                        st.rerun()
                else:
                    if st.button("Remove Location"):
                        st.session_state.locations.remove(st.session_state.location)
                        database.update_user_locations(conn, st.session_state.username, st.session_state.locations)
                        st.success(f"{st.session_state.location} removed from your locations")
                        st.rerun()
        elif aqi_data and 'error' in aqi_data and 'suggestions' in aqi_data:
            # Display city suggestions
            st.error(f"Location '{st.session_state.location}' not found. Did you mean one of these?")
            
            # Display city suggestions as buttons
            suggestions = aqi_data.get('suggestions', [])
            if suggestions:
                cols = st.columns(min(3, len(suggestions)))
                for i, suggestion in enumerate(suggestions[:6]):  # Show up to 6 suggestions
                    col_idx = i % len(cols)
                    with cols[col_idx]:
                        if st.button(f"📍 {suggestion}", key=f"suggestion_{i}"):
                            st.session_state.location = suggestion
                            st.rerun()
            
            st.info("Please select a location from the suggestions or try a different search term.")
            
            # Display a list of popular cities to try
            st.subheader("Popular Cities")
            popular_cities = ["Shanghai", "Delhi", "Paris", "Berlin", "New York", "Los Angeles", 
                             "Tokyo", "Seoul", "Beijing", "Mumbai", "London", "Bangkok"]
            
            # Create a grid of buttons for popular cities
            cols = st.columns(3)
            for i, city in enumerate(popular_cities):
                col_idx = i % 3
                with cols[col_idx]:
                    if st.button(f"🌆 {city}", key=f"popular_{i}"):
                        st.session_state.location = city
                        st.rerun()
        elif aqi_data and 'aqi' in aqi_data:
            # Display pollutants data
            st.subheader("Pollutant Levels")
            
            pollutants = aqi_data.get('pollutants', {})
            if pollutants:
                pollutant_names = list(pollutants.keys())
                pollutant_values = [pollutants[p] for p in pollutant_names]
                
                fig = px.bar(
                    x=pollutant_names,
                    y=pollutant_values,
                    labels={'x': 'Pollutant', 'y': 'Concentration (μg/m³)'},
                    color=pollutant_values,
                    color_continuous_scale=['green', 'yellow', 'orange', 'red'],
                    title="Pollutant Concentrations"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Add description of pollutants
                with st.expander("Learn about these pollutants"):
                    st.markdown("""
                    - **PM2.5**: Fine particulate matter that can penetrate deep into the lungs and bloodstream
                    - **PM10**: Coarse particulate matter that can enter the respiratory system
                    - **O3**: Ozone at ground level can trigger respiratory problems
                    - **NO2**: Nitrogen Dioxide mainly from vehicle emissions, can cause respiratory inflammation
                    - **SO2**: Sulfur Dioxide from fossil fuel combustion, can cause respiratory issues
                    - **CO**: Carbon Monoxide, reduces oxygen delivery to organs
                    """)
            else:
                st.info("Detailed pollutant data not available for this location")
            
            # Quick health recommendations based on AQI
            aqi_value = aqi_data.get('aqi', 0)
            st.subheader("Quick Health Tips")
            recommendations = get_recommendations(aqi_value)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("General Advice")
                st.write(recommendations['general'])
                
                st.subheader("Outdoor Activities")
                st.write(recommendations['outdoor'])
            
            with col2:
                st.subheader("Protection Measures")
                st.write(recommendations['protection'])
                
                st.subheader("Health Watch")
                st.write(recommendations['health'])
            
            # Save AQI data to database for history
            database.save_aqi_reading(conn, st.session_state.username, st.session_state.location, aqi_value, aqi_data)
            
        else:
            st.error("Failed to fetch air quality data. Please check the location name or try again later.")
    
    with tab2:
        st.title("Historical AQI Data")
        st.write("Track air quality trends over time")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", datetime.now() - timedelta(days=7))
        with col2:
            end_date = st.date_input("End date", datetime.now())
        
        if start_date > end_date:
            st.error("Start date cannot be after end date")
        else:
            # Fetch historical data
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
                
                # Line chart
                fig = px.line(
                    df, 
                    x='timestamp', 
                    y='aqi', 
                    title=f"AQI Trend for {st.session_state.location}",
                    labels={'timestamp': 'Date', 'aqi': 'AQI Value'},
                    markers=True
                )
                
                # Add color zones for AQI categories
                fig.add_hrect(y0=0, y1=50, line_width=0, fillcolor="green", opacity=0.2)
                fig.add_hrect(y0=50, y1=100, line_width=0, fillcolor="yellow", opacity=0.2)
                fig.add_hrect(y0=100, y1=150, line_width=0, fillcolor="orange", opacity=0.2)
                fig.add_hrect(y0=150, y1=200, line_width=0, fillcolor="red", opacity=0.2)
                fig.add_hrect(y0=200, y1=300, line_width=0, fillcolor="purple", opacity=0.2)
                fig.add_hrect(y0=300, y1=500, line_width=0, fillcolor="maroon", opacity=0.2)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Statistics
                st.subheader("Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Average AQI", round(df['aqi'].mean(), 1))
                
                with col2:
                    st.metric("Maximum AQI", df['aqi'].max())
                
                with col3:
                    st.metric("Minimum AQI", df['aqi'].min())
                
                # AQI category breakdown
                df['category'] = df['aqi'].apply(lambda x: utils.get_aqi_category(x)[0])
                category_counts = df['category'].value_counts().reset_index()
                category_counts.columns = ['Category', 'Days']
                
                fig = px.pie(
                    category_counts, 
                    values='Days', 
                    names='Category',
                    title="AQI Category Distribution",
                    color='Category',
                    color_discrete_map={
                        'Good': 'green',
                        'Moderate': 'yellow',
                        'Unhealthy for Sensitive Groups': 'orange',
                        'Unhealthy': 'red',
                        'Very Unhealthy': 'purple',
                        'Hazardous': 'maroon'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.info("No historical data available for this location and date range")
    
    with tab3:
        st.title("User Profile")
        
        # User information
        st.subheader("Account Information")
        st.write(f"**Username:** {st.session_state.username}")
        join_date = database.get_user_join_date(conn, st.session_state.username)
        st.write(f"**Member since:** {join_date}")
        
        # Saved locations
        st.subheader("Saved Locations")
        
        if st.session_state.locations:
            for i, location in enumerate(st.session_state.locations):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📍 {location}")
                with col2:
                    if st.button("View", key=f"view_{i}"):
                        st.session_state.location = location
                        st.rerun()
        else:
            st.info("You haven't saved any locations yet. Search for a location and click 'Save Location' to add it here.")
        
        # Account preferences
        st.subheader("Preferences")
        
        default_unit = database.get_user_preference(conn, st.session_state.username, "unit") or "metric"
        unit_system = st.selectbox(
            "Unit System",
            options=["metric", "imperial"],
            index=0 if default_unit == "metric" else 1
        )
        
        if st.button("Save Preferences"):
            database.update_user_preference(conn, st.session_state.username, "unit", unit_system)
            st.success("Preferences updated!")
    
    with tab4:
        st.title("Health Recommendations")
        
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
            st.write(detailed_recs['general_detailed'])
            
            # Specific recommendations for different groups
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
            
            # Long-term health impacts
            st.subheader("Health Impact Information")
            st.write(detailed_recs['health_impacts'])
            
            # AI-generated personalized recommendations
            st.subheader("AI Health Assistant")
            
            user_health_condition = st.text_input("Do you have any specific health conditions? (e.g., asthma, COPD, heart disease)")
            
            if user_health_condition:
                personalized_advice = utils.get_personalized_recommendation(aqi_value, user_health_condition)
                st.write(personalized_advice)
            else:
                st.info("Enter your health conditions to receive personalized recommendations")
            
        else:
            st.info("Please select a location to view health recommendations")

# Footer
st.markdown("---")
st.markdown("AirQual - AI Air Quality Monitoring System")
st.markdown("Data sources: OpenAQ and other air quality monitoring networks")
