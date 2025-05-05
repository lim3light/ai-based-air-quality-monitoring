import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import re

# API URLs
WAQI_BASE_URL = "https://api.waqi.info"
import os
# Get API key from environment variables
WAQI_API_KEY = os.environ.get("WAQI_API_KEY", "demo")

def get_current_aqi(location):
    """
    Fetch current Air Quality Index for a location
    
    Args:
        location (str): City name
        
    Returns:
        dict: Dictionary containing AQI and pollutant data
    """
    try:
        # Clean the location name - remove special characters and ensure it's properly formatted
        location = clean_location_name(location)
        
        # Fetch data directly from WAQI API
        api_url = f"{WAQI_BASE_URL}/feed/{location}/?token={WAQI_API_KEY}"
        response = requests.get(api_url)
        data = response.json()
        
        if data['status'] == 'ok':
            aqi = data['data']['aqi']
            
            # Extract pollutants
            pollutants = {}
            iaqi = data['data'].get('iaqi', {})
            
            # Map common pollutants
            pollutant_map = {
                'pm25': 'PM2.5',
                'pm10': 'PM10',
                'o3': 'O3',
                'no2': 'NO2',
                'so2': 'SO2',
                'co': 'CO'
            }
            
            for key, display_name in pollutant_map.items():
                if key in iaqi:
                    pollutants[display_name] = iaqi[key]['v']
            
            # Get location name from the API response
            display_location = data['data']['city'].get('name', location)
            
            return {
                'aqi': aqi,
                'pollutants': pollutants,
                'location': display_location,
                'timestamp': datetime.now().isoformat(),
                'dominentpol': data['data'].get('dominentpol', 'unknown')
            }
        else:
            # If this specific city name didn't work, try to find similar cities
            similar_cities = search_city(location)
            if similar_cities:
                # We don't want to automatically choose a city - we'll provide suggestions
                # Return None with suggestions
                return {
                    'error': 'City not found',
                    'suggestions': similar_cities[:5]  # Return top 5 suggestions
                }
            return None
            
    except Exception as e:
        print(f"Error fetching AQI data: {e}")
        return None

def clean_location_name(location):
    """
    Clean the location name for API query
    
    Args:
        location (str): Raw location name input
        
    Returns:
        str: Cleaned location name
    """
    # Remove special characters except for spaces
    location = re.sub(r'[^\w\s]', '', location)
    # Replace spaces with URL-friendly format
    location = location.replace(' ', '%20')
    return location

def search_city(keyword):
    """
    Search for cities by keyword
    
    Args:
        keyword (str): Search keyword
        
    Returns:
        list: List of matching city names
    """
    try:
        search_url = f"{WAQI_BASE_URL}/search/?token={WAQI_API_KEY}&keyword={keyword}"
        response = requests.get(search_url)
        data = response.json()
        
        if data['status'] == 'ok' and 'data' in data:
            # Extract city names from search results
            cities = []
            for item in data['data']:
                if 'station' in item and 'name' in item['station']:
                    cities.append(item['station']['name'])
            return cities
        return []
    except Exception as e:
        print(f"Error searching cities: {e}")
        return []

def calculate_aqi(pollutants):
    """
    Calculate AQI based on pollutant concentrations
    This is a simplified calculation for demonstration purposes
    """
    # If we have PM2.5, use it as the primary indicator (simplified approach)
    if 'pm25' in pollutants:
        pm25 = pollutants['pm25']
        # Simple linear mapping for PM2.5 to AQI (simplified)
        if pm25 <= 12:
            return int(50 * (pm25 / 12))
        elif pm25 <= 35.4:
            return int(50 + (50 * (pm25 - 12) / 23.4))
        elif pm25 <= 55.4:
            return int(100 + (50 * (pm25 - 35.4) / 20))
        elif pm25 <= 150.4:
            return int(150 + (50 * (pm25 - 55.4) / 95))
        elif pm25 <= 250.4:
            return int(200 + (100 * (pm25 - 150.4) / 100))
        else:
            return int(300 + (200 * (pm25 - 250.4) / 250))
    
    # Alternative calculation using PM10 if PM2.5 is not available
    elif 'pm10' in pollutants:
        pm10 = pollutants['pm10']
        if pm10 <= 54:
            return int(50 * (pm10 / 54))
        elif pm10 <= 154:
            return int(50 + (50 * (pm10 - 54) / 100))
        elif pm10 <= 254:
            return int(100 + (50 * (pm10 - 154) / 100))
        elif pm10 <= 354:
            return int(150 + (50 * (pm10 - 254) / 100))
        elif pm10 <= 424:
            return int(200 + (100 * (pm10 - 354) / 70))
        else:
            return int(300 + (200 * (pm10 - 424) / 176))
    
    # Fallback to NO2 or O3 with very simple mapping
    elif 'no2' in pollutants:
        return min(300, int(pollutants['no2'] * 2))
    elif 'o3' in pollutants:
        return min(300, int(pollutants['o3'] * 1.5))
    
    # Default AQI if no relevant pollutants are available
    return 50  # Assume moderate air quality when data is incomplete

def get_historical_aqi(location, days=7):
    """
    Fetch historical AQI data for a location from database or API
    
    Args:
        location (str): City name
        days (int): Number of days of historical data to retrieve
        
    Returns:
        list: List of dictionaries with historical AQI readings
    """
    try:
        # Clean the location name for API query
        location = clean_location_name(location)
        
        # Get current AQI first to check if the location exists
        api_url = f"{WAQI_BASE_URL}/feed/{location}/?token={WAQI_DEMO_TOKEN}"
        response = requests.get(api_url)
        data = response.json()
        
        if data['status'] != 'ok':
            return None
        
        # Extract forecast data which contains historical data
        forecast_data = data['data'].get('forecast', {}).get('daily', {})
        
        # Process historical data
        historical_aqi = []
        
        # Get PM2.5 historical data
        if 'pm25' in forecast_data:
            pm25_data = forecast_data['pm25']
            for entry in pm25_data:
                if 'day' in entry and 'avg' in entry:
                    day = entry['day']
                    avg = entry['avg']
                    
                    pollutants = {'PM2.5': avg}
                    
                    # Find matching PM10 data for the same day if available
                    if 'pm10' in forecast_data:
                        for pm10_entry in forecast_data['pm10']:
                            if pm10_entry.get('day') == day:
                                pollutants['PM10'] = pm10_entry['avg']
                                break
                    
                    # Find matching O3 data for the same day if available
                    if 'o3' in forecast_data:
                        for o3_entry in forecast_data['o3']:
                            if o3_entry.get('day') == day:
                                pollutants['O3'] = o3_entry['avg']
                                break
                    
                    # Calculate AQI (in this case, we can use the avg value directly as it's already the AQI)
                    historical_aqi.append({
                        'date': day,
                        'aqi': avg,  # Using PM2.5 average as AQI
                        'pollutants': pollutants,
                        'timestamp': datetime.strptime(day, "%Y-%m-%d").isoformat()
                    })
        
        # Sort by date
        historical_aqi.sort(key=lambda x: x['date'], reverse=True)
        
        return historical_aqi[:days]  # Return only the requested number of days
        
    except Exception as e:
        print(f"Error fetching historical AQI: {e}")
        return None
