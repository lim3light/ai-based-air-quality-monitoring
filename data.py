import requests
import pandas as pd
import time
from datetime import datetime, timedelta

# OpenAQ API base URL
OPENAQ_BASE_URL = "https://api.openaq.org/v2"

def get_current_aqi(location):
    """
    Fetch current Air Quality Index for a location
    
    Args:
        location (str): City name
        
    Returns:
        dict: Dictionary containing AQI and pollutant data
    """
    try:
        # First, get the location coordinates
        location_url = f"{OPENAQ_BASE_URL}/locations"
        location_params = {
            "limit": 1,
            "page": 1,
            "offset": 0,
            "sort": "desc",
            "radius": 1000,
            "name": location,
            "order_by": "lastUpdated"
        }
        
        location_response = requests.get(location_url, params=location_params)
        location_data = location_response.json()
        
        if not location_data or 'results' not in location_data or not location_data['results']:
            return None
        
        location_id = location_data['results'][0]['id']
        
        # Now get the latest measurements for this location
        measurements_url = f"{OPENAQ_BASE_URL}/latest/{location_id}"
        measurements_response = requests.get(measurements_url)
        measurements_data = measurements_response.json()
        
        if not measurements_data or 'results' not in measurements_data or not measurements_data['results']:
            return None
        
        pollutants = {}
        for measurement in measurements_data['results']:
            parameter = measurement['parameter']
            value = measurement['value']
            pollutants[parameter] = value
        
        # Calculate AQI based on pollutants
        # Note: This is a simplified calculation, a real-world system would use more complex AQI formulas
        aqi = calculate_aqi(pollutants)
        
        return {
            'aqi': aqi,
            'pollutants': pollutants,
            'location': location,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Error fetching AQI data: {e}")
        # Fallback to alternative API or mock data for testing
        try:
            # Try alternative API (WAQI/AirVisual)
            return get_aqi_from_alternative_source(location)
        except:
            return None

def get_aqi_from_alternative_source(location):
    """
    Fallback to an alternative API for AQI data
    """
    try:
        # Example using World Air Quality Index API (requires API key in production)
        api_url = f"https://api.waqi.info/feed/{location}/?token=demo"
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
            
            return {
                'aqi': aqi,
                'pollutants': pollutants,
                'location': location,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        print(f"Error with alternative AQI source: {e}")
        return None

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
    Fetch historical AQI data for a location
    """
    try:
        # In a real implementation, you would fetch historical data from an API
        # For this example, we'll create some simulated historical data
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # First, get the location details
        location_url = f"{OPENAQ_BASE_URL}/locations"
        location_params = {
            "limit": 1,
            "page": 1,
            "offset": 0,
            "sort": "desc",
            "radius": 1000,
            "name": location,
            "order_by": "lastUpdated"
        }
        
        location_response = requests.get(location_url, params=location_params)
        location_data = location_response.json()
        
        if not location_data or 'results' not in location_data or not location_data['results']:
            return None
        
        location_id = location_data['results'][0]['id']
        
        # Now get historical measurements
        measurements_url = f"{OPENAQ_BASE_URL}/measurements"
        measurements_params = {
            "location_id": location_id,
            "date_from": start_date.isoformat(),
            "date_to": end_date.isoformat(),
            "limit": 1000,
            "page": 1,
            "offset": 0,
            "sort": "desc",
            "parameter": ["pm25", "pm10", "o3", "no2", "so2", "co"]
        }
        
        measurements_response = requests.get(measurements_url, params=measurements_params)
        measurements_data = measurements_response.json()
        
        if not measurements_data or 'results' not in measurements_data:
            return None
        
        # Process the historical data
        results = measurements_data['results']
        
        # Group by date and calculate daily AQI
        df = pd.DataFrame(results)
        if df.empty:
            return None
        
        # Convert date string to datetime
        df['date'] = pd.to_datetime(df['date']['utc'])
        df['date'] = df['date'].dt.date
        
        # Group by date and parameter
        grouped = df.groupby(['date', 'parameter'])['value'].mean().reset_index()
        
        # Pivot to get parameters as columns
        pivoted = grouped.pivot(index='date', columns='parameter', values='value').reset_index()
        
        # Calculate AQI for each day
        historical_aqi = []
        for _, row in pivoted.iterrows():
            pollutants = {}
            for param in row.index:
                if param != 'date' and not pd.isna(row[param]):
                    pollutants[param] = row[param]
            
            if pollutants:
                aqi = calculate_aqi(pollutants)
                historical_aqi.append({
                    'date': row['date'],
                    'aqi': aqi,
                    'pollutants': pollutants
                })
        
        return historical_aqi
        
    except Exception as e:
        print(f"Error fetching historical AQI: {e}")
        return None
