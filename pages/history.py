import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database
import utils
from utils import get_aqi_category

# Page configuration
st.set_page_config(
    page_title="AirQual - Historical Data",
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
    st.warning("Please login to access historical data")
    st.stop()

# Get database connection
conn = database.get_connection()

# Sidebar
with st.sidebar:
    st.title("🌬️ AirQual")
    st.subheader("Historical Data")
    
    # Location selector
    st.subheader("Select Location")
    
    # Get user's saved locations
    user_data = database.get_user_data(conn, st.session_state.username)
    saved_locations = user_data.get('saved_locations', []) if user_data else []
    
    if saved_locations:
        location = st.selectbox(
            "Choose from saved locations",
            options=saved_locations,
            index=saved_locations.index(st.session_state.location) if st.session_state.location in saved_locations else 0
        )
    else:
        location = st.text_input("Enter location", value=st.session_state.location)
    
    if st.button("Set Location"):
        st.session_state.location = location
        st.rerun()
    
    # Date range selector
    st.subheader("Date Range")
    
    # Preset options
    preset = st.selectbox(
        "Preset ranges",
        options=["Last 7 days", "Last 30 days", "Last 3 months", "Custom range"]
    )
    
    if preset == "Last 7 days":
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
    elif preset == "Last 30 days":
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
    elif preset == "Last 3 months":
        start_date = datetime.now() - timedelta(days=90)
        end_date = datetime.now()
    else:  # Custom range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start date", datetime.now() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End date", datetime.now())
    
    # Visualization options
    st.subheader("Visualization Options")
    chart_type = st.selectbox(
        "Chart type",
        options=["Line chart", "Bar chart", "Heat map"]
    )
    
    show_trends = st.checkbox("Show trends", value=True)
    show_categories = st.checkbox("Show AQI categories", value=True)

# Main content
st.title(f"Historical Air Quality Data: {st.session_state.location}")

# Date validation
if start_date > end_date:
    st.error("Start date cannot be after end date")
    st.stop()

# Fetch historical data
with st.spinner("Fetching historical data..."):
    historical_data = database.get_historical_aqi(
        conn, 
        st.session_state.username, 
        st.session_state.location,
        start_date,
        end_date
    )

if not historical_data:
    st.info(f"No historical data available for {st.session_state.location} in the selected date range.")
    
    # Options to generate data
    st.write("To build your historical data:")
    st.write("1. Visit the dashboard regularly to automatically collect data")
    st.write("2. Set up automatic data collection (coming soon)")
    
    if st.button("Go to Dashboard"):
        st.switch_page("pages/dashboard.py")
else:
    # Convert to DataFrame for analysis
    df = pd.DataFrame(historical_data)
    
    # Ensure timestamp is datetime
    if 'timestamp' in df.columns and df['timestamp'].dtype != 'datetime64[ns]':
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Add category information
    df['category'] = df['aqi'].apply(lambda x: get_aqi_category(x)[0])
    df['color'] = df['aqi'].apply(lambda x: get_aqi_category(x)[1])
    
    # Summary statistics
    st.subheader("Summary Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Average AQI", round(df['aqi'].mean(), 1))
    
    with col2:
        st.metric("Maximum AQI", round(df['aqi'].max(), 1))
    
    with col3:
        st.metric("Minimum AQI", round(df['aqi'].min(), 1))
    
    with col4:
        # Most frequent category
        category_counts = df['category'].value_counts()
        most_common_category = category_counts.index[0]
        st.metric("Most Common", most_common_category)
    
    # Main visualization
    st.subheader("AQI Trend Over Time")
    
    if chart_type == "Line chart":
        fig = px.line(
            df, 
            x='timestamp', 
            y='aqi',
            labels={'timestamp': 'Date', 'aqi': 'AQI Value'},
            markers=True
        )
        
        # Add trendline if requested
        if show_trends and len(df) > 3:
            fig.add_trace(
                px.scatter(df, x='timestamp', y='aqi', trendline="lowess").data[1]
            )
        
        # Add category zones if requested
        if show_categories:
            fig.add_hrect(y0=0, y1=50, line_width=0, fillcolor="green", opacity=0.1)
            fig.add_hrect(y0=50, y1=100, line_width=0, fillcolor="yellow", opacity=0.1)
            fig.add_hrect(y0=100, y1=150, line_width=0, fillcolor="orange", opacity=0.1)
            fig.add_hrect(y0=150, y1=200, line_width=0, fillcolor="red", opacity=0.1)
            fig.add_hrect(y0=200, y1=300, line_width=0, fillcolor="purple", opacity=0.1)
            fig.add_hrect(y0=300, y1=500, line_width=0, fillcolor="maroon", opacity=0.1)
            
            # Add category labels
            fig.add_annotation(x=df['timestamp'].min(), y=25, text="Good", showarrow=False, xanchor="left")
            fig.add_annotation(x=df['timestamp'].min(), y=75, text="Moderate", showarrow=False, xanchor="left")
            fig.add_annotation(x=df['timestamp'].min(), y=125, text="Unhealthy for Sensitive Groups", showarrow=False, xanchor="left")
            fig.add_annotation(x=df['timestamp'].min(), y=175, text="Unhealthy", showarrow=False, xanchor="left")
            fig.add_annotation(x=df['timestamp'].min(), y=250, text="Very Unhealthy", showarrow=False, xanchor="left")
            fig.add_annotation(x=df['timestamp'].min(), y=400, text="Hazardous", showarrow=False, xanchor="left")
        
    elif chart_type == "Bar chart":
        # Aggregate by day for bar chart
        df['date'] = df['timestamp'].dt.date
        daily_avg = df.groupby('date')['aqi'].mean().reset_index()
        daily_avg['category'] = daily_avg['aqi'].apply(lambda x: get_aqi_category(x)[0])
        daily_avg['color'] = daily_avg['aqi'].apply(lambda x: get_aqi_category(x)[1])
        
        fig = px.bar(
            daily_avg,
            x='date',
            y='aqi',
            color='category',
            color_discrete_map={
                'Good': '#4CAF50',
                'Moderate': '#FFEB3B',
                'Unhealthy for Sensitive Groups': '#FF9800',
                'Unhealthy': '#F44336',
                'Very Unhealthy': '#9C27B0',
                'Hazardous': '#800000'
            },
            labels={'date': 'Date', 'aqi': 'Average Daily AQI'}
        )
        
        # Add reference lines for AQI categories
        if show_categories:
            fig.add_hline(y=50, line_dash="dash", line_color="green", opacity=0.7)
            fig.add_hline(y=100, line_dash="dash", line_color="yellow", opacity=0.7)
            fig.add_hline(y=150, line_dash="dash", line_color="orange", opacity=0.7)
            fig.add_hline(y=200, line_dash="dash", line_color="red", opacity=0.7)
            fig.add_hline(y=300, line_dash="dash", line_color="purple", opacity=0.7)
    
    elif chart_type == "Heat map":
        # Create a heatmap of AQI by day and hour
        if len(df) >= 24:  # Need at least a day of data
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour
            
            # Create pivot table
            pivot = df.pivot_table(
                index='date', 
                columns='hour', 
                values='aqi', 
                aggfunc='mean'
            ).fillna(0)
            
            # Create heatmap
            fig = px.imshow(
                pivot,
                labels={'x': 'Hour of Day', 'y': 'Date', 'color': 'AQI'},
                x=[str(h) for h in range(24)],
                color_continuous_scale=[
                    '#4CAF50',  # Green
                    '#FFEB3B',  # Yellow
                    '#FF9800',  # Orange
                    '#F44336',  # Red
                    '#9C27B0',  # Purple
                    '#800000'   # Maroon
                ],
                aspect="auto"
            )
            
            fig.update_layout(
                xaxis_title="Hour of Day",
                yaxis_title="Date"
            )
        else:
            st.warning("Not enough data for a heatmap view. Try a different chart type or date range.")
            # Fall back to line chart
            fig = px.line(
                df, 
                x='timestamp', 
                y='aqi',
                labels={'timestamp': 'Date', 'aqi': 'AQI Value'},
                markers=True
            )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Add data breakdown section
    with st.expander("Data Breakdown"):
        # AQI category distribution
        st.subheader("AQI Category Distribution")
        
        category_counts = df['category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        
        # Calculate percentages
        total_readings = len(df)
        category_counts['Percentage'] = (category_counts['Count'] / total_readings * 100).round(1)
        
        # Order categories by AQI severity
        category_order = [
            'Good', 
            'Moderate', 
            'Unhealthy for Sensitive Groups', 
            'Unhealthy', 
            'Very Unhealthy', 
            'Hazardous'
        ]
        
        # Create ordered DataFrame
        ordered_cats = []
        for cat in category_order:
            if cat in category_counts['Category'].values:
                cat_data = category_counts[category_counts['Category'] == cat].iloc[0]
                ordered_cats.append({
                    'Category': cat,
                    'Count': cat_data['Count'],
                    'Percentage': cat_data['Percentage']
                })
        
        if ordered_cats:
            ordered_df = pd.DataFrame(ordered_cats)
            
            # Display as pie chart
            fig = px.pie(
                ordered_df,
                values='Count',
                names='Category',
                title="AQI Category Distribution",
                color='Category',
                color_discrete_map={
                    'Good': '#4CAF50',
                    'Moderate': '#FFEB3B',
                    'Unhealthy for Sensitive Groups': '#FF9800',
                    'Unhealthy': '#F44336',
                    'Very Unhealthy': '#9C27B0',
                    'Hazardous': '#800000'
                }
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display as table
            st.dataframe(
                ordered_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Data table with raw readings
        st.subheader("Raw Data")
        
        display_df = df[['timestamp', 'aqi', 'category']].sort_values('timestamp', ascending=False)
        display_df = display_df.rename(columns={'timestamp': 'Time', 'aqi': 'AQI', 'category': 'Category'})
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Download Data as CSV",
            csv,
            f"aqi_data_{st.session_state.location}_{start_date.strftime('%Y%m%d')}_to_{end_date.strftime('%Y%m%d')}.csv",
            "text/csv",
            key='download-csv'
        )
