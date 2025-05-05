import os
import psycopg2
from psycopg2.extras import Json
from datetime import datetime
import json

def get_connection():
    """
    Get a connection to the PostgreSQL database
    """
    try:
        # Get connection details from environment variables
        host = os.getenv("PGHOST")
        port = os.getenv("PGPORT")
        user = os.getenv("PGUSER")
        password = os.getenv("PGPASSWORD")
        database = os.getenv("PGDATABASE")
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        
        # Create tables if they don't exist
        initialize_database(conn)
        
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        # Return None or raise an exception based on your error handling strategy
        return None

def initialize_database(conn):
    """
    Create required tables if they don't exist
    """
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(50) PRIMARY KEY,
        password VARCHAR(256) NOT NULL,
        created_at TIMESTAMP NOT NULL,
        last_login TIMESTAMP
    )
    """)
    
    # Create user preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        username VARCHAR(50) PRIMARY KEY REFERENCES users(username),
        saved_locations JSONB DEFAULT '[]'::jsonb,
        unit VARCHAR(10) DEFAULT 'metric',
        notification_preferences JSONB DEFAULT '{}'::jsonb
    )
    """)
    
    # Create AQI readings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS aqi_readings (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) REFERENCES users(username),
        location VARCHAR(100) NOT NULL,
        aqi_value FLOAT NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        pollutants JSONB,
        data JSONB
    )
    """)
    
    # Create password resets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS password_resets (
        username VARCHAR(50) REFERENCES users(username),
        token VARCHAR(64) NOT NULL,
        expiry TIMESTAMP NOT NULL,
        PRIMARY KEY (username, token)
    )
    """)
    
    conn.commit()

def get_user_data(conn, username):
    """
    Get user data and preferences
    """
    if not conn:
        return None
        
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.username, u.created_at, p.saved_locations, p.unit, p.notification_preferences
    FROM users u
    LEFT JOIN user_preferences p ON u.username = p.username
    WHERE u.username = %s
    """, (username,))
    
    result = cursor.fetchone()
    
    if not result:
        return None
    
    username, created_at, saved_locations, unit, notification_preferences = result
    
    # Convert JSONB to Python dicts/lists
    if saved_locations:
        saved_locations = json.loads(saved_locations)
    else:
        saved_locations = []
        
    if notification_preferences:
        notification_preferences = json.loads(notification_preferences)
    else:
        notification_preferences = {}
        
    return {
        'username': username,
        'created_at': created_at,
        'saved_locations': saved_locations,
        'unit': unit,
        'notification_preferences': notification_preferences
    }

def update_user_locations(conn, username, locations):
    """
    Update a user's saved locations
    """
    if not conn:
        return False
        
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE user_preferences
        SET saved_locations = %s
        WHERE username = %s
        """, (Json(locations), username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user locations: {e}")
        conn.rollback()
        return False

def get_user_preference(conn, username, preference):
    """
    Get a specific user preference
    """
    if not conn:
        return None
        
    cursor = conn.cursor()
    
    if preference == 'saved_locations':
        cursor.execute("""
        SELECT saved_locations
        FROM user_preferences
        WHERE username = %s
        """, (username,))
    elif preference == 'unit':
        cursor.execute("""
        SELECT unit
        FROM user_preferences
        WHERE username = %s
        """, (username,))
    elif preference == 'notification_preferences':
        cursor.execute("""
        SELECT notification_preferences
        FROM user_preferences
        WHERE username = %s
        """, (username,))
    else:
        return None
        
    result = cursor.fetchone()
    
    if not result:
        return None
        
    value = result[0]
    
    # Convert JSONB to Python objects if needed
    if preference in ['saved_locations', 'notification_preferences'] and value:
        return json.loads(value)
    
    return value

def update_user_preference(conn, username, preference, value):
    """
    Update a specific user preference
    """
    if not conn:
        return False
        
    cursor = conn.cursor()
    try:
        if preference == 'saved_locations':
            cursor.execute("""
            UPDATE user_preferences
            SET saved_locations = %s
            WHERE username = %s
            """, (Json(value), username))
        elif preference == 'unit':
            cursor.execute("""
            UPDATE user_preferences
            SET unit = %s
            WHERE username = %s
            """, (value, username))
        elif preference == 'notification_preferences':
            cursor.execute("""
            UPDATE user_preferences
            SET notification_preferences = %s
            WHERE username = %s
            """, (Json(value), username))
        else:
            return False
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating user preference: {e}")
        conn.rollback()
        return False

def save_aqi_reading(conn, username, location, aqi_value, data):
    """
    Save an AQI reading to the database
    """
    if not conn:
        return False
        
    cursor = conn.cursor()
    try:
        pollutants = data.get('pollutants', {})
        timestamp = datetime.now()
        
        cursor.execute("""
        INSERT INTO aqi_readings (username, location, aqi_value, timestamp, pollutants, data)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (username, location, aqi_value, timestamp, Json(pollutants), Json(data)))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error saving AQI reading: {e}")
        conn.rollback()
        return False

def get_historical_aqi(conn, username, location, start_date, end_date):
    """
    Get historical AQI readings for a user and location within a date range
    """
    if not conn:
        return []
        
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT timestamp, aqi_value, pollutants
        FROM aqi_readings
        WHERE username = %s AND location = %s AND timestamp::date BETWEEN %s AND %s
        ORDER BY timestamp
        """, (username, location, start_date, end_date))
        
        results = cursor.fetchall()
        
        if not results:
            return []
            
        historical_data = []
        for timestamp, aqi_value, pollutants in results:
            historical_data.append({
                'timestamp': timestamp,
                'aqi': aqi_value,
                'pollutants': json.loads(pollutants) if pollutants else {}
            })
            
        return historical_data
    except Exception as e:
        print(f"Error retrieving historical AQI: {e}")
        return []

def get_user_join_date(conn, username):
    """
    Get the date a user joined
    """
    if not conn:
        return None
        
    cursor = conn.cursor()
    cursor.execute("""
    SELECT created_at
    FROM users
    WHERE username = %s
    """, (username,))
    
    result = cursor.fetchone()
    
    if not result:
        return None
        
    join_date = result[0]
    return join_date.strftime("%B %d, %Y")

def update_last_login(conn, username):
    """
    Update a user's last login timestamp
    """
    if not conn:
        return False
        
    cursor = conn.cursor()
    try:
        cursor.execute("""
        UPDATE users
        SET last_login = %s
        WHERE username = %s
        """, (datetime.now(), username))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error updating last login: {e}")
        conn.rollback()
        return False
