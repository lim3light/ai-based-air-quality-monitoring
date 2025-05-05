import hashlib
import secrets
import string
from datetime import datetime

def hash_password(password):
    """
    Hash a password for storing.
    """
    salt = hashlib.sha256(secrets.token_bytes(32)).hexdigest()
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                  salt.encode('utf-8'), 100000)
    pwdhash = pwdhash.hex()
    return salt + pwdhash

def verify_password(stored_password, provided_password):
    """
    Verify a stored password against one provided by user
    """
    salt = stored_password[:64]
    stored_hash = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), 
                                  salt.encode('utf-8'), 100000)
    pwdhash = pwdhash.hex()
    return pwdhash == stored_hash

def register_user(conn, username, password):
    """
    Register a new user
    """
    # Check if username already exists
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
    if cursor.fetchone():
        return False
    
    # Hash the password
    hashed_password = hash_password(password)
    
    # Insert new user
    try:
        cursor.execute(
            "INSERT INTO users (username, password, created_at) VALUES (%s, %s, %s)",
            (username, hashed_password, datetime.now())
        )
        conn.commit()
        
        # Create user preferences entry
        cursor.execute(
            "INSERT INTO user_preferences (username, unit) VALUES (%s, %s)",
            (username, "metric")
        )
        conn.commit()
        
        return True
    except Exception as e:
        print(f"Error registering user: {e}")
        conn.rollback()
        return False

def verify_user(conn, username, password):
    """
    Verify user credentials
    """
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    
    if not result:
        return False
    
    stored_password = result[0]
    return verify_password(stored_password, password)

def generate_reset_token():
    """
    Generate a token for password reset
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def save_reset_token(conn, username, token, expiry):
    """
    Save reset token to database
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO password_resets (username, token, expiry) VALUES (%s, %s, %s)",
        (username, token, expiry)
    )
    conn.commit()

def verify_reset_token(conn, token):
    """
    Verify a reset token
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, expiry FROM password_resets WHERE token = %s",
        (token,)
    )
    result = cursor.fetchone()
    
    if not result:
        return None
    
    username, expiry = result
    
    if datetime.now() > expiry:
        return None
    
    return username

def update_password(conn, username, new_password):
    """
    Update a user's password
    """
    hashed_password = hash_password(new_password)
    
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = %s WHERE username = %s",
        (hashed_password, username)
    )
    conn.commit()
    
    # Remove used token
    cursor.execute(
        "DELETE FROM password_resets WHERE username = %s",
        (username,)
    )
    conn.commit()
