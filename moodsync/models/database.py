import sqlite3
from datetime import datetime
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DatabaseManager:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create tables
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    first_name VARCHAR(50),
                    last_name VARCHAR(50),
                    profile_image VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS moods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    detected_emotion VARCHAR(50),
                    confidence_score FLOAT,
                    manual_mood VARCHAR(50),
                    intensity INTEGER,
                    notes TEXT,
                    context VARCHAR(100),
                    image_path VARCHAR(255),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                );
                
                CREATE TABLE IF NOT EXISTS suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood_id INTEGER,
                    suggestion_type VARCHAR(50),
                    content TEXT,
                    used BOOLEAN DEFAULT FALSE,
                    helpful_rating INTEGER,
                    FOREIGN KEY (mood_id) REFERENCES moods (id)
                );
                
                -- Insert default user if not exists
                INSERT OR IGNORE INTO users (id, username, email, password_hash) 
                VALUES (1, 'default_user', 'user@moodsync.com', 'pbkdf2:sha256:150000$default_hash');
            ''')
            
            conn.commit()
    
    def log_mood(self, user_id=1, emotion=None, confidence=None, manual_mood=None, intensity=None, notes=None, context=None, image_path=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO moods (user_id, detected_emotion, confidence_score, manual_mood, intensity, notes, context, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, emotion, confidence, manual_mood, intensity, notes, context, image_path))
            
            mood_id = cursor.lastrowid
            conn.commit()
            return mood_id
    
    def save_suggestions(self, mood_id, suggestions):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for suggestion in suggestions:
                cursor.execute('''
                    INSERT INTO suggestions (mood_id, suggestion_type, content)
                    VALUES (?, ?, ?)
                ''', (mood_id, suggestion['type'], suggestion['content']))
            
            conn.commit()
    
    def get_mood_history(self, user_id=1, days=7, limit=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM moods 
                WHERE user_id = ? AND timestamp >= datetime('now', '-' || ? || ' days')
                ORDER BY timestamp DESC
            '''
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (user_id, days))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_mood_stats(self, user_id=1, days=30):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get emotion counts
            cursor.execute('''
                SELECT detected_emotion, COUNT(*) as count
                FROM moods
                WHERE user_id = ? AND timestamp >= datetime('now', '-' || ? || ' days')
                GROUP BY detected_emotion
                ORDER BY count DESC
            ''', (user_id, days))
            
            emotion_counts = [dict(row) for row in cursor.fetchall()]
            
            # Get daily mood averages (using intensity as a proxy for mood score)
            cursor.execute('''
                SELECT date(timestamp) as date, AVG(intensity) as avg_intensity
                FROM moods
                WHERE user_id = ? AND timestamp >= datetime('now', '-' || ? || ' days') AND intensity IS NOT NULL
                GROUP BY date(timestamp)
                ORDER BY date
            ''', (user_id, days))
            
            daily_mood = [dict(row) for row in cursor.fetchall()]
            
            return {
                'emotion_counts': emotion_counts,
                'daily_mood': daily_mood
            }
    
    def get_suggestion_effectiveness(self, user_id=1):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.suggestion_type, AVG(s.helpful_rating) as avg_rating, COUNT(*) as count
                FROM suggestions s
                JOIN moods m ON s.mood_id = m.id
                WHERE m.user_id = ? AND s.helpful_rating IS NOT NULL
                GROUP BY s.suggestion_type
                ORDER BY avg_rating DESC
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def rate_suggestion(self, suggestion_id, rating):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE suggestions
                SET helpful_rating = ?, used = TRUE
                WHERE id = ?
            ''', (rating, suggestion_id))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_user_profile(self, user_id=1):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, username, email, first_name, last_name, profile_image, created_at FROM users WHERE id = ?', (user_id,))
            return dict(cursor.fetchone())
            
    def register_user(self, username, email, password_hash, first_name=None, last_name=None):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, first_name, last_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, email, password_hash, first_name, last_name))
                
                user_id = cursor.lastrowid
                conn.commit()
                return user_id
        except sqlite3.IntegrityError:
            # Username or email already exists
            return None
    
    def get_user_by_username(self, username):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            return dict(user) if user else None
    
    def get_user_by_email(self, email):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            user = cursor.fetchone()
            return dict(user) if user else None
            
    def update_user_profile(self, user_id, first_name=None, last_name=None, profile_image=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically based on provided fields
            update_fields = []
            params = []
            
            if first_name is not None:
                update_fields.append('first_name = ?')
                params.append(first_name)
                
            if last_name is not None:
                update_fields.append('last_name = ?')
                params.append(last_name)
                
            if profile_image is not None:
                update_fields.append('profile_image = ?')
                params.append(profile_image)
                
            if not update_fields:
                return False
                
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            params.append(user_id)
            
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
