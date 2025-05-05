import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
import utils

# Page configuration
st.set_page_config(
    page_title="AirQual - User Profile",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state if needed
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Check authentication
if not st.session_state.authenticated:
    st.warning("Please login to access your profile")
    st.stop()

# Get database connection
conn = database.get_connection()

# Sidebar
with st.sidebar:
    st.title("🌬️ AirQual")
    st.subheader("User Profile")
    
    # Navigation options
    st.subheader("Profile Sections")
    section = st.radio(
        "Go to:",
        ["Account Information", "Saved Locations", "Preferences", "Usage Statistics"]
    )

# Main content
st.title("User Profile")
st.write(f"Welcome back, {st.session_state.username}!")

if section == "Account Information":
    st.header("Account Information")
    
    # Basic user info
    user_data = database.get_user_data(conn, st.session_state.username)
    
    if user_data:
        st.subheader("Your Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Username:** {user_data['username']}")
            join_date = user_data['created_at'].strftime("%B %d, %Y") if user_data['created_at'] else "Unknown"
            st.write(f"**Member since:** {join_date}")
        
        with col2:
            st.write(f"**Preferred units:** {user_data['unit'].capitalize()}")
            locations_count = len(user_data['saved_locations']) if user_data['saved_locations'] else 0
            st.write(f"**Saved locations:** {locations_count}")
    
    # Account actions
    st.subheader("Account Actions")
    
    # Change password option
    with st.expander("Change Password"):
        current_password = st.text_input("Current Password", type="password", key="current_pwd")
        new_password = st.text_input("New Password", type="password", key="new_pwd")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pwd")
        
        if st.button("Update Password"):
            if new_password != confirm_password:
                st.error("New passwords do not match")
            elif not current_password or not new_password:
                st.error("Please fill in all password fields")
            else:
                # Verify current password
                if database.auth.verify_user(conn, st.session_state.username, current_password):
                    # Update password
                    database.auth.update_password(conn, st.session_state.username, new_password)
                    st.success("Password updated successfully!")
                else:
                    st.error("Current password is incorrect")

elif section == "Saved Locations":
    st.header("Saved Locations")
    
    # Get user's saved locations
    user_data = database.get_user_data(conn, st.session_state.username)
    saved_locations = user_data.get('saved_locations', []) if user_data else []
    
    if saved_locations:
        st.write("Here are all your saved locations for quick access to air quality data:")
        
        # Create a grid layout for locations
        col_count = 3
        cols = st.columns(col_count)
        
        for i, location in enumerate(saved_locations):
            col_index = i % col_count
            
            with cols[col_index]:
                st.markdown(
                    f"""
                    <div style="border:1px solid #ddd;padding:15px;border-radius:5px;margin-bottom:10px;">
                        <h3 style="margin:0;">{location}</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("View", key=f"view_{i}"):
                        st.session_state.location = location
                        # Redirect to dashboard
                        st.switch_page("pages/dashboard.py")
                
                with col2:
                    if st.button("Remove", key=f"remove_{i}"):
                        saved_locations.remove(location)
                        database.update_user_locations(conn, st.session_state.username, saved_locations)
                        st.success(f"Removed {location} from your saved locations")
                        st.rerun()
        
        # Add new location
        st.subheader("Add New Location")
        new_location = st.text_input("Enter city name")
        
        if st.button("Add Location") and new_location:
            if new_location not in saved_locations:
                saved_locations.append(new_location)
                database.update_user_locations(conn, st.session_state.username, saved_locations)
                st.success(f"Added {new_location} to your saved locations")
                st.rerun()
            else:
                st.warning(f"{new_location} is already in your saved locations")
    
    else:
        st.info("You haven't saved any locations yet.")
        
        st.subheader("Add Your First Location")
        new_location = st.text_input("Enter city name")
        
        if st.button("Add Location") and new_location:
            database.update_user_locations(conn, st.session_state.username, [new_location])
            st.success(f"Added {new_location} to your saved locations")
            st.rerun()

elif section == "Preferences":
    st.header("User Preferences")
    
    # Get current preferences
    user_data = database.get_user_data(conn, st.session_state.username)
    current_unit = user_data.get('unit', 'metric') if user_data else 'metric'
    notification_prefs = user_data.get('notification_preferences', {}) if user_data else {}
    
    # Unit preference
    st.subheader("Measurement Units")
    unit_system = st.selectbox(
        "Preferred unit system",
        options=["metric", "imperial"],
        index=0 if current_unit == "metric" else 1
    )
    
    # Notification preferences
    st.subheader("Notification Preferences")
    
    notify_high_aqi = st.checkbox(
        "Notify me when AQI exceeds a threshold",
        value=notification_prefs.get('high_aqi_enabled', False)
    )
    
    high_aqi_threshold = 100
    if notify_high_aqi:
        high_aqi_threshold = st.slider(
            "AQI threshold for notifications",
            min_value=50,
            max_value=300,
            value=notification_prefs.get('high_aqi_threshold', 100),
            step=10
        )
    
    # Display preferences
    st.subheader("Display Preferences")
    
    default_dashboard_view = st.selectbox(
        "Default dashboard view",
        options=["Current AQI", "Historical Trend", "Pollutant Breakdown"],
        index=0  # Default to Current AQI
    )
    
    # Save preferences
    if st.button("Save Preferences"):
        # Update unit preference
        database.update_user_preference(conn, st.session_state.username, "unit", unit_system)
        
        # Update notification preferences
        notification_prefs = {
            'high_aqi_enabled': notify_high_aqi,
            'high_aqi_threshold': high_aqi_threshold,
            'dashboard_default_view': default_dashboard_view
        }
        
        database.update_user_preference(conn, st.session_state.username, "notification_preferences", notification_prefs)
        
        st.success("Preferences updated successfully!")

elif section == "Usage Statistics":
    st.header("Your Usage Statistics")
    
    # Date range selector for statistics
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("To", datetime.now())
    
    if start_date > end_date:
        st.error("Start date cannot be after end date")
    else:
        # Get all user locations
        user_data = database.get_user_data(conn, st.session_state.username)
        all_locations = user_data.get('saved_locations', []) if user_data else []
        
        if not all_locations:
            st.info("You haven't saved any locations yet. Add locations to see usage statistics.")
        else:
            # Get all AQI readings for the user in the date range
            readings_by_location = {}
            
            for location in all_locations:
                historical_data = database.get_historical_aqi(
                    conn, 
                    st.session_state.username, 
                    location,
                    start_date,
                    end_date
                )
                
                if historical_data:
                    readings_by_location[location] = historical_data
            
            if not readings_by_location:
                st.info("No data available for the selected date range.")
            else:
                # Total readings count
                total_readings = sum(len(readings) for readings in readings_by_location.values())
                st.metric("Total Air Quality Readings", total_readings)
                
                # Locations with data
                st.subheader("Locations Monitored")
                
                # Create a DataFrame with location stats
                stats_data = []
                
                for location, readings in readings_by_location.items():
                    if readings:
                        df = pd.DataFrame(readings)
                        stats_data.append({
                            'Location': location,
                            'Readings': len(df),
                            'Avg AQI': round(df['aqi'].mean(), 1),
                            'Max AQI': df['aqi'].max(),
                            'Min AQI': df['aqi'].min()
                        })
                
                if stats_data:
                    stats_df = pd.DataFrame(stats_data)
                    st.dataframe(stats_df, use_container_width=True)
                    
                    # Most monitored location
                    most_monitored = stats_df.loc[stats_df['Readings'].idxmax()]
                    st.write(f"Your most monitored location is **{most_monitored['Location']}** with **{most_monitored['Readings']}** readings.")
                    
                    # Location with best/worst air quality
                    best_air = stats_df.loc[stats_df['Avg AQI'].idxmin()]
                    worst_air = stats_df.loc[stats_df['Avg AQI'].idxmax()]
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Best air quality:** {best_air['Location']} (Avg AQI: {best_air['Avg AQI']})")
                    
                    with col2:
                        st.write(f"**Worst air quality:** {worst_air['Location']} (Avg AQI: {worst_air['Avg AQI']})")
