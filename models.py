import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from datetime import datetime, timedelta
import os

class AQIPredictor:
    """
    Machine learning model for predicting AQI trends
    """
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
    
    def train(self, historical_data):
        """
        Train the model on historical AQI data
        
        Args:
            historical_data (list): List of dictionaries with historical AQI readings
        
        Returns:
            bool: True if training was successful, False otherwise
        """
        if not historical_data or len(historical_data) < 10:
            return False
        
        # Create DataFrame from historical data
        df = pd.DataFrame(historical_data)
        
        # Ensure timestamp is datetime
        if df['timestamp'].dtype != 'datetime64[ns]':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract features from datetime
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['hour'] = df['timestamp'].dt.hour
        df['month'] = df['timestamp'].dt.month
        df['day'] = df['timestamp'].dt.day
        
        # Engineer additional features
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week']/7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week']/7)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour']/24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour']/24)
        
        # Add lag features (previous day's AQI)
        df['aqi_1d_lag'] = df['aqi'].shift(1)
        df['aqi_2d_lag'] = df['aqi'].shift(2)
        df['aqi_7d_lag'] = df['aqi'].shift(7)
        
        # Handle missing values from shifting
        df = df.dropna()
        
        if df.empty or len(df) < 8:
            return False
        
        # Select features and target
        features = ['day_of_week', 'hour', 'month', 'day', 
                    'day_sin', 'day_cos', 'hour_sin', 'hour_cos',
                    'aqi_1d_lag', 'aqi_2d_lag', 'aqi_7d_lag']
        
        X = df[features]
        y = df['aqi']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Normalize features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        if self.model_type == 'random_forest':
            self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model trained with MSE: {mse}, R²: {r2}")
        
        return True
    
    def predict(self, historical_data, days_ahead=5, hours_per_day=4):
        """
        Predict future AQI values
        
        Args:
            historical_data (list): Recent historical data for prediction
            days_ahead (int): Number of days to predict
            hours_per_day (int): Number of hours per day to predict
            
        Returns:
            list: Predicted AQI values with timestamps
        """
        if not self.model:
            return None
        
        if not historical_data or len(historical_data) < 8:
            return None
        
        # Create DataFrame from recent data
        df = pd.DataFrame(historical_data)
        
        # Ensure timestamp is datetime
        if df['timestamp'].dtype != 'datetime64[ns]':
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp
        df = df.sort_values('timestamp')
        
        # Get most recent data point
        last_timestamp = df['timestamp'].max()
        
        # Prepare data for forecasting
        forecast_times = []
        for day in range(days_ahead):
            for hour in range(0, 24, 24 // hours_per_day):
                forecast_times.append(last_timestamp + timedelta(days=day+1, hours=hour))
        
        # Create forecast DataFrame
        forecast_df = pd.DataFrame({'timestamp': forecast_times})
        
        # Extract features
        forecast_df['day_of_week'] = forecast_df['timestamp'].dt.dayofweek
        forecast_df['hour'] = forecast_df['timestamp'].dt.hour
        forecast_df['month'] = forecast_df['timestamp'].dt.month
        forecast_df['day'] = forecast_df['timestamp'].dt.day
        
        # Engineer features
        forecast_df['day_sin'] = np.sin(2 * np.pi * forecast_df['day_of_week']/7)
        forecast_df['day_cos'] = np.cos(2 * np.pi * forecast_df['day_of_week']/7)
        forecast_df['hour_sin'] = np.sin(2 * np.pi * forecast_df['hour']/24)
        forecast_df['hour_cos'] = np.cos(2 * np.pi * forecast_df['hour']/24)
        
        # Get lag values from historical data
        last_aqi = df['aqi'].iloc[-1]
        second_last_aqi = df['aqi'].iloc[-2] if len(df) > 1 else last_aqi
        seventh_last_aqi = df['aqi'].iloc[-7] if len(df) > 6 else last_aqi
        
        # Initialize with historical values
        forecast_df['aqi_1d_lag'] = last_aqi
        forecast_df['aqi_2d_lag'] = second_last_aqi
        forecast_df['aqi_7d_lag'] = seventh_last_aqi
        
        # Select features
        features = ['day_of_week', 'hour', 'month', 'day', 
                   'day_sin', 'day_cos', 'hour_sin', 'hour_cos',
                   'aqi_1d_lag', 'aqi_2d_lag', 'aqi_7d_lag']
        
        # Make predictions step by step
        predictions = []
        current_df = forecast_df.copy()
        
        # Predict each time step
        for i in range(len(forecast_times)):
            # Get features for current prediction
            X = current_df.iloc[i:i+1][features]
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            pred = self.model.predict(X_scaled)[0]
            pred = max(0, pred)  # Ensure non-negative AQI
            
            # Store prediction
            predictions.append({
                'timestamp': forecast_times[i].isoformat(),
                'aqi': round(pred, 1)
            })
            
            # Update lag values for next prediction
            if i+1 < len(forecast_times):
                if (i+1) % hours_per_day == 0:  # New day
                    current_df.loc[i+1:, 'aqi_1d_lag'] = pred
                if (i+1) % (hours_per_day*2) == 0:  # Every 2 days
                    current_df.loc[i+1:, 'aqi_2d_lag'] = pred
                if (i+1) % (hours_per_day*7) == 0:  # Every 7 days
                    current_df.loc[i+1:, 'aqi_7d_lag'] = pred
        
        return predictions
    
    def save_model(self, path='aqi_model.joblib'):
        """
        Save the trained model to a file
        """
        if not self.model:
            return False
        
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'model_type': self.model_type
            }
            joblib.dump(model_data, path)
            return True
        except Exception as e:
            print(f"Error saving model: {e}")
            return False
    
    def load_model(self, path='aqi_model.joblib'):
        """
        Load a trained model from a file
        """
        try:
            if not os.path.exists(path):
                return False
                
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.model_type = model_data['model_type']
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
