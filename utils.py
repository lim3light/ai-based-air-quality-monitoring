import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
import streamlit as st

def get_aqi_category(aqi_value):
    """
    Determine AQI category and color based on value
    
    Args:
        aqi_value (float): AQI value
        
    Returns:
        tuple: (category_name, color_code)
    """
    if aqi_value <= 50:
        return "Good", "#4CAF50"  # Green
    elif aqi_value <= 100:
        return "Moderate", "#FFEB3B"  # Yellow
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups", "#FF9800"  # Orange
    elif aqi_value <= 200:
        return "Unhealthy", "#F44336"  # Red
    elif aqi_value <= 300:
        return "Very Unhealthy", "#9C27B0"  # Purple
    else:
        return "Hazardous", "#800000"  # Maroon

def predict_aqi_trend(historical_data, days_to_predict=3):
    """
    Predict AQI trend for the next few days based on historical data
    
    Args:
        historical_data (list): List of dictionaries with historical AQI readings
        days_to_predict (int): Number of days to predict
        
    Returns:
        list: Predicted AQI values
    """
    if not historical_data or len(historical_data) < 5:
        return None
    
    # Create DataFrame from historical data
    df = pd.DataFrame(historical_data)
    
    # Convert timestamp to datetime if it's not already
    if df['timestamp'].dtype != 'datetime64[ns]':
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract features from datetime
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['day'] = df['timestamp'].dt.day
    
    # Features and target
    X = df[['day_of_week', 'month', 'day']]
    y = df['aqi']
    
    # Train a RandomForest model
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    # Generate dates for prediction
    last_date = df['timestamp'].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(days_to_predict)]
    
    # Create features for prediction
    future_features = pd.DataFrame({
        'day_of_week': [date.dayofweek for date in future_dates],
        'month': [date.month for date in future_dates],
        'day': [date.day for date in future_dates]
    })
    
    # Make predictions
    predictions = model.predict(future_features)
    
    # Return predictions with dates
    return [
        {'date': future_dates[i].strftime('%Y-%m-%d'), 'aqi': max(0, round(predictions[i], 1))}
        for i in range(len(predictions))
    ]

def get_personalized_recommendation(aqi, health_condition):
    """
    Generate personalized health recommendations based on AQI and health condition
    
    Args:
        aqi (float): Current AQI value
        health_condition (str): User's health condition
        
    Returns:
        str: Personalized recommendation
    """
    condition_lower = health_condition.lower()
    
    # Base advice based on AQI level
    if aqi <= 50:
        base_advice = "Air quality is good. It's a great day for outdoor activities."
    elif aqi <= 100:
        base_advice = "Air quality is moderate. Most people can continue outdoor activities."
    elif aqi <= 150:
        base_advice = "Air quality is unhealthy for sensitive groups. Consider reducing prolonged outdoor exertion."
    elif aqi <= 200:
        base_advice = "Air quality is unhealthy. Everyone should reduce prolonged outdoor exertion."
    elif aqi <= 300:
        base_advice = "Air quality is very unhealthy. Avoid outdoor activities when possible."
    else:
        base_advice = "Air quality is hazardous. Avoid all outdoor activities."
    
    # Specific advice based on health condition
    specific_advice = ""
    
    if 'asthma' in condition_lower or 'copd' in condition_lower or 'respiratory' in condition_lower:
        if aqi <= 50:
            specific_advice = "With your respiratory condition, you should be comfortable outside today, but always keep your rescue inhaler available."
        elif aqi <= 100:
            specific_advice = "For people with asthma or COPD, watch for any symptoms while outdoors. Consider keeping outdoor activities moderate in duration."
        elif aqi <= 150:
            specific_advice = "With your respiratory condition, you should limit prolonged outdoor activities and keep medication handy. Consider wearing an N95 mask if you must be outside."
        else:
            specific_advice = "Given your respiratory condition, it's strongly advised to stay indoors with windows closed and air purifier running. If you must go outside, wear an N95 mask and limit exposure time."
    
    elif 'heart' in condition_lower or 'cardiovascular' in condition_lower:
        if aqi <= 50:
            specific_advice = "With your heart condition, today's air quality is good for your regular outdoor activities."
        elif aqi <= 100:
            specific_advice = "For those with heart issues, maintain awareness of your exertion level and any unusual symptoms."
        elif aqi <= 150:
            specific_advice = "With your cardiovascular condition, consider indoor exercise today or reducing intensity of outdoor activities."
        else:
            specific_advice = "Given your heart condition, avoid outdoor exertion today. Air pollution can increase stress on your cardiovascular system."
    
    elif 'allerg' in condition_lower:
        if aqi <= 50:
            specific_advice = "Allergy sufferers should still monitor personal symptoms, but air quality today is generally favorable."
        elif aqi <= 100:
            specific_advice = "For allergy sufferers, consider taking your allergy medication before going outdoors today."
        elif aqi <= 150:
            specific_advice = "With your allergies, consider wearing a mask outside and taking allergy medication beforehand."
        else:
            specific_advice = "Given your allergy sensitivity, stay indoors with windows closed and air purifier running if possible."
    
    elif 'pregna' in condition_lower:
        if aqi <= 50:
            specific_advice = "For expectant mothers, today's air quality is good for normal outdoor activities."
        elif aqi <= 100:
            specific_advice = "Pregnant women should monitor how they feel during outdoor activities and take breaks as needed."
        elif aqi <= 150:
            specific_advice = "As an expectant mother, consider limiting prolonged outdoor exposure today to protect both you and your baby."
        else:
            specific_advice = "For the health of you and your baby, it's advised to stay indoors today and keep windows closed."
    
    else:
        # Generic advice for other/unspecified conditions
        if aqi > 100:
            specific_advice = "Given your health situation, pay close attention to any unusual symptoms when outdoors and reduce exposure time if needed."
    
    if specific_advice:
        return f"{base_advice}\n\nPersonalized advice: {specific_advice}"
    else:
        return base_advice

def format_timestamp(timestamp):
    """
    Format a timestamp for display
    """
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    
    return timestamp.strftime("%B %d, %Y at %H:%M")
