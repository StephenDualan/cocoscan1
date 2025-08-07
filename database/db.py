import sqlite3
import os
from datetime import datetime

def get_db_path():
    """Get the database file path for mobile storage"""
    try:
        # For mobile, store in app's private directory
        from kivy.utils import platform
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                db_dir = app_storage_path()
            except ImportError:
                # Fallback for development
                db_dir = os.path.dirname(os.path.abspath(__file__))
        else:
            db_dir = os.path.dirname(os.path.abspath(__file__))
    except ImportError:
        # Fallback when Kivy is not available (for testing)
        db_dir = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(db_dir, 'cocoscan.db')

def init_db():
    """Initialize the database and create all tables if they don't exist"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    ''')
    
    # Create scans table with more detailed information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            leaf_type TEXT NOT NULL,
            health_status TEXT NOT NULL,
            confidence REAL NOT NULL,
            image_path TEXT,
            notes TEXT,
            location TEXT,
            weather_conditions TEXT,
            scan_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create leaf_types table for categorization
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaf_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            scientific_name TEXT,
            description TEXT,
            common_diseases TEXT
        )
    ''')
    
    # Create health_statuses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_statuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status TEXT UNIQUE NOT NULL,
            description TEXT,
            severity_level INTEGER DEFAULT 1
        )
    ''')
    
    # Insert default leaf types - Coconut focused
    default_leaf_types = [
        ('Coconut', 'Cocos nucifera', 'Coconut palm leaves - Primary focus', 'Lethal yellowing, Root wilt, Bud rot, Stem bleeding'),
        ('Coconut Seedling', 'Cocos nucifera', 'Young coconut plant leaves', 'Nutrient deficiency, Root rot, Leaf spot'),
        ('Coconut Mature', 'Cocos nucifera', 'Mature coconut palm leaves', 'Lethal yellowing, Root wilt, Anthracnose'),
        ('Coconut Hybrid', 'Cocos nucifera', 'Hybrid coconut varieties', 'Disease resistance, Yield optimization'),
        ('Other Palm', 'Arecaceae', 'Other palm species', 'Various palm diseases')
    ]
    
    for leaf_type in default_leaf_types:
        cursor.execute('''
            INSERT OR IGNORE INTO leaf_types (name, scientific_name, description, common_diseases)
            VALUES (?, ?, ?, ?)
        ''', leaf_type)
    
    # Insert default health statuses
    default_statuses = [
        ('Healthy', 'Leaf appears healthy with no visible disease', 1),
        ('Mild Disease', 'Minor disease symptoms detected', 2),
        ('Moderate Disease', 'Moderate disease symptoms present', 3),
        ('Severe Disease', 'Severe disease symptoms detected', 4),
        ('Critical', 'Critical disease state requiring immediate attention', 5)
    ]
    
    for status in default_statuses:
        cursor.execute('''
            INSERT OR IGNORE INTO health_statuses (status, description, severity_level)
            VALUES (?, ?, ?)
        ''', status)
    
    conn.commit()
    conn.close()

def create_user(username, password_hash, email=None):
    """Create a new user account"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', (username, password_hash, email))
        
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None  # Username already exists
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def verify_user(username, password_hash):
    """Verify user credentials and return user_id if valid"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        result = cursor.fetchone()
        
        if result:
            user_id = result[0]
            # Update last login
            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
        
        cursor.close()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def save_scan(user_id, leaf_type, health_status, confidence, image_path=None, 
              notes=None, location=None, weather_conditions=None):
    """Save detailed scan result to database"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans (user_id, leaf_type, health_status, confidence, 
                              image_path, notes, location, weather_conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, leaf_type, health_status, confidence, image_path, 
              notes, location, weather_conditions))
        
        scan_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return scan_id
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def save_scan_with_error(user_id, leaf_type, health_status, confidence, image_path=None, 
              notes=None, location=None, weather_conditions=None):
    """Save detailed scan result to database, return (scan_id, error_message)"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans (user_id, leaf_type, health_status, confidence, 
                              image_path, notes, location, weather_conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, leaf_type, health_status, confidence, image_path, 
              notes, location, weather_conditions))
        
        scan_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        return scan_id, None
    except Exception as e:
        return None, str(e)

def get_user_scans(user_id, limit=50):
    """Get scan history for a specific user"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, leaf_type, health_status, confidence, image_path, 
                   notes, location, weather_conditions, scan_date
            FROM scans 
            WHERE user_id = ?
            ORDER BY scan_date DESC
            LIMIT ?
        ''', (user_id, limit))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Database Error: {e}")
        return []

def get_all_scans(limit=100):
    """Get all scan history (for admin purposes)"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.id, u.username, s.leaf_type, s.health_status, s.confidence,
                   s.image_path, s.notes, s.location, s.weather_conditions, s.scan_date
            FROM scans s
            LEFT JOIN users u ON s.user_id = u.id
            ORDER BY s.scan_date DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Database Error: {e}")
        return []

def get_scan_statistics(user_id=None):
    """Get statistics about scans"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if user_id:
            # User-specific statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_scans,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN health_status = 'Healthy' THEN 1 END) as healthy_count,
                    COUNT(CASE WHEN health_status != 'Healthy' THEN 1 END) as diseased_count
                FROM scans 
                WHERE user_id = ?
            ''', (user_id,))
        else:
            # Overall statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_scans,
                    AVG(confidence) as avg_confidence,
                    COUNT(CASE WHEN health_status = 'Healthy' THEN 1 END) as healthy_count,
                    COUNT(CASE WHEN health_status != 'Healthy' THEN 1 END) as diseased_count
                FROM scans
            ''')
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'total_scans': result[0],
                'avg_confidence': round(result[1], 2) if result[1] else 0,
                'healthy_count': result[2],
                'diseased_count': result[3]
            }
        return None
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def get_leaf_types():
    """Get all available leaf types"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, scientific_name, description FROM leaf_types ORDER BY name')
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Database Error: {e}")
        return []

def get_health_statuses():
    """Get all available health statuses"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT status, description, severity_level FROM health_statuses ORDER BY severity_level')
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Database Error: {e}")
        return []

def delete_scan(scan_id, user_id=None):
    """Delete a scan (only if user owns it or admin)"""
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('DELETE FROM scans WHERE id = ? AND user_id = ?', (scan_id, user_id))
        else:
            cursor.execute('DELETE FROM scans WHERE id = ?', (scan_id,))
        
        deleted = cursor.rowcount > 0
        conn.commit()
        cursor.close()
        conn.close()
        return deleted
    except Exception as e:
        print(f"Database Error: {e}")
        return False

# Legacy functions for backward compatibility
def save_to_db(result, confidence, image_path=None):
    """Legacy function - save scan result to SQLite database"""
    return save_scan(None, 'Unknown', result, confidence, image_path)

def get_scan_history():
    """Legacy function - get all scan history from database"""
    return get_all_scans()
