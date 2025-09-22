from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import base64
import uuid
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from models.emotion_detector import EmotionDetector
from models.ai_suggestions import SuggestionEngine
from models.database import DatabaseManager
from config import Config
from emotion_api import load_emotion_model, initialize_face_detection, extract_features

# Database connection function
def get_db_connection():
    import os
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'moodsync.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
db_manager = DatabaseManager()
emotion_detector = EmotionDetector()
suggestion_engine = SuggestionEngine()

# Set secret key
app.secret_key = 'moodsync_secret_key'

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/home')
@login_required
def home():
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get mood statistics
    mood_stats = db_manager.get_mood_stats(user_id=user_id, days=30)
    
    return render_template('home.html', mood_stats=mood_stats)

@app.route('/save_journal', methods=['POST'])
@login_required
def save_journal():
    entry_text = request.json.get('entry_text')
    user_id = session.get('user_id')
    
    if not entry_text:
        return jsonify({'error': 'Journal entry cannot be empty'}), 400
    
    # In a real implementation, you would save this to the database
    # db_manager.save_journal_entry(user_id, entry_text)
    
    return jsonify({'success': True, 'message': 'Journal entry saved successfully'})

@app.route('/get_journal_entries')
@login_required
def get_journal_entries():
    user_id = session.get('user_id')
    
    # In a real implementation, you would fetch entries from the database
    # entries = db_manager.get_journal_entries(user_id)
    
    # For demo purposes, return empty list
    return jsonify({'entries': []})

@app.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    user_id = session.get('user_id')
    timeframe = request.json.get('timeframe', 'week')
    
    # In a real implementation, you would generate the report data here
    # report_data = db_manager.generate_mood_report(user_id, timeframe)
    
    # For demo purposes, return success
    return jsonify({'success': True, 'message': 'Report generated successfully'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        # Validate form data
        if not username or not email or not password or not confirm_password:
            flash('All fields are required', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
            
        # Check if username or email already exists
        if db_manager.get_user_by_username(username):
            flash('Username already exists', 'danger')
            return render_template('register.html')
            
        if db_manager.get_user_by_email(email):
            flash('Email already exists', 'danger')
            return render_template('register.html')
            
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Register user
        user_id = db_manager.register_user(username, email, password_hash, first_name, last_name)
        
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed. Please try again.', 'danger')
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('login.html')
            
        user = db_manager.get_user_by_username(username)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            # store first_name for navbar display
            session['first_name'] = user.get('first_name') if isinstance(user, dict) else user['first_name'] if 'first_name' in user.keys() else None
            
            # Set session expiry for remember me
            if remember:
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=30)
            
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
                
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get recent mood history (last week, few items)
    mood_history = db_manager.get_mood_history(user_id=user_id, days=7, limit=5)
    
    # Charts/statistics base window
    mood_stats = db_manager.get_mood_stats(user_id=user_id, days=30)
    
    # Card summary - use a wider window so cards are populated even if last 30d are sparse
    card_window = db_manager.get_mood_stats(user_id=user_id, days=365)
    card_stats = {
        'total_entries': card_window.get('total_entries', 0) if isinstance(card_window, dict) else 0,
        'average_intensity': (card_window.get('average_intensity') or 0.0) if isinstance(card_window, dict) else 0.0,
        'dominant_emotion': card_window.get('dominant_emotion') if isinstance(card_window, dict) else None,
        'streak': card_window.get('streak', 0) if isinstance(card_window, dict) else 0,
    }
    
    return render_template('dashboard.html', 
                           mood_history=mood_history, 
                           mood_stats=mood_stats,
                           card_stats=card_stats)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    user_id = session.get('user_id')
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        # Add flash message for all form submissions
        flash('Settings updated successfully!', 'success')
        
        if form_type == 'profile':
            # Handle profile form
            name = request.form.get('name')
            email = request.form.get('email')
            age = request.form.get('age')
            gender = request.form.get('gender')
            bio = request.form.get('bio', '')
            
            # Validate inputs
            if not name or not email:
                flash('Name and email are required', 'danger')
                return redirect(url_for('settings'))
                
            # Validate age
            if age:
                try:
                    age = int(age)
                    if age < 1 or age > 120:
                        flash('Age must be between 1 and 120', 'danger')
                        return redirect(url_for('settings'))
                except ValueError:
                    flash('Invalid age value', 'danger')
                    return redirect(url_for('settings'))
            
            # Validate gender
            if gender and gender not in ['male', 'female', 'other', 'prefer_not_to_say']:
                flash('Invalid gender value', 'danger')
                return redirect(url_for('settings'))
            
            # Update user profile
            conn = get_db_connection()
            
            try:
                # Check if bio column exists
                try:
                    conn.execute('SELECT bio FROM users WHERE id = ?', (user_id,))
                except sqlite3.OperationalError:
                    # Add bio column if it doesn't exist
                    conn.execute('ALTER TABLE users ADD COLUMN bio TEXT')
                
                # Update user profile
                conn.execute('UPDATE users SET name = ?, email = ?, bio = ? WHERE id = ?', 
                            (name, email, bio, user_id))
                conn.commit()
                flash('Profile updated successfully', 'success')
            except sqlite3.Error as e:
                flash(f'Failed to update profile: {str(e)}', 'danger')
            
            conn.close()
        
        elif form_type == 'preferences':
            # Handle preferences form
            theme = request.form.get('theme')
            dashboard_layout = request.form.get('dashboard_layout')
            show_suggestions = 'show_suggestions' in request.form
            
            # Update preferences in database
            conn = get_db_connection()
            
            try:
                # Check if preferences exist for user
                prefs = conn.execute('SELECT * FROM preferences WHERE user_id = ?', (user_id,)).fetchone()
                
                if prefs:
                    conn.execute('UPDATE preferences SET theme = ?, dashboard_layout = ?, show_suggestions = ? WHERE user_id = ?',
                                (theme, dashboard_layout, show_suggestions, user_id))
                else:
                    conn.execute('INSERT INTO preferences (user_id, theme, dashboard_layout, show_suggestions) VALUES (?, ?, ?, ?)',
                                (user_id, theme, dashboard_layout, show_suggestions))
                
                conn.commit()
                flash('Preferences updated successfully', 'success')
            except sqlite3.Error as e:
                # Create preferences table if it doesn't exist
                conn.executescript('''
                    CREATE TABLE IF NOT EXISTS preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        theme VARCHAR(20) DEFAULT 'light',
                        dashboard_layout VARCHAR(20) DEFAULT 'grid',
                        show_suggestions BOOLEAN DEFAULT 1,
                        language VARCHAR(10) DEFAULT 'en',
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    );
                ''')                
                conn.executescript('''
                    CREATE TABLE IF NOT EXISTS preferences (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        theme VARCHAR(20) DEFAULT 'light',
                        dashboard_layout VARCHAR(20) DEFAULT 'grid',
                        show_suggestions BOOLEAN DEFAULT 1,
                        language VARCHAR(10) DEFAULT 'en',
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    );
                ''')                
                # Try again after creating the table
                try:
                    conn.execute('INSERT INTO preferences (user_id, theme, dashboard_layout, show_suggestions, language) VALUES (?, ?, ?, ?, ?)',
                                (user_id, theme, dashboard_layout, show_suggestions, request.form.get('language', 'en')))
                    conn.commit()
                    flash('Preferences updated successfully', 'success')
                except sqlite3.Error as e:
                    flash(f'Failed to update preferences: {str(e)}', 'danger')
            finally:
                conn.close()
                
        elif form_type == 'connected_accounts':
            # Handle connected accounts form
            flash('Connected accounts settings updated successfully', 'success')
            
        elif form_type == 'subscription':
            # Handle subscription form
            flash('Subscription settings updated successfully', 'success')
            
        elif form_type == 'download_data':
            # Handle data download
            # In a real implementation, you would generate a JSON file with user data
            flash('Your data is being prepared for download', 'success')
        
        elif form_type == 'account':
            # Handle account updates
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate inputs
            if not current_password or not new_password or not confirm_password:
                flash('All password fields are required', 'danger')
                return redirect(url_for('settings'))
                
            if new_password != confirm_password:
                flash('New passwords do not match', 'danger')
                return redirect(url_for('settings'))
            
            # Verify current password
            conn = get_db_connection()
            user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            
            from werkzeug.security import check_password_hash, generate_password_hash
            
            if not check_password_hash(user['password_hash'], current_password):
                flash('Current password is incorrect', 'danger')
                conn.close()
                return redirect(url_for('settings'))
                
            # Update password
            hashed_password = generate_password_hash(new_password)
            conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (hashed_password, user_id))
            conn.commit()
            conn.close()
            
            flash('Password updated successfully', 'success')
    
    # Get user data for the settings page
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    
    # Get user preferences (if preferences table exists)
    try:
        user_prefs = conn.execute('SELECT * FROM preferences WHERE user_id = ?', (user_id,)).fetchone()
    except sqlite3.OperationalError:
        # If preferences table doesn't exist yet
        user_prefs = None
        
        # Create preferences table
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                theme VARCHAR(20) DEFAULT 'light',
                dashboard_layout VARCHAR(20) DEFAULT 'grid',
                show_suggestions BOOLEAN DEFAULT 1,
                language VARCHAR(10) DEFAULT 'en',
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        ''')
        
        # Insert default preferences for user
        conn.execute('INSERT INTO preferences (user_id, theme, dashboard_layout, show_suggestions, language) VALUES (?, ?, ?, ?, ?)',
                    (user_id, 'light', 'standard', 1, 'en'))
        conn.commit()
        
        # Get the newly created preferences
        user_prefs = conn.execute('SELECT * FROM preferences WHERE user_id = ?', (user_id,)).fetchone()
    
    conn.close()
    return render_template('settings.html', user=user_data, preferences=user_prefs)
        
@app.route('/detect_emotion', methods=['POST'])
@login_required
def detect_emotion():
    if 'image_data' not in request.json:
        return jsonify({'error': 'No image data provided'}), 400
    
    # Get user ID from session
    user_id = session.get('user_id')
    
    image_data = request.json['image_data']
    
    # Detect emotion from image
    emotion, confidence = emotion_detector.detect_emotion_from_image(image_data)
    
    if emotion is None:
        return jsonify({'error': 'No face detected'}), 400
    
    # Save image if requested
    image_path = None
    if request.json.get('save_image', False):
        # Create a unique filename
        filename = f"{emotion.lower()}_{uuid.uuid4().hex}.jpg"
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save base64 image to file
        image_data_clean = image_data.split(',')[1] if ',' in image_data else image_data
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data_clean))
        
        # Store relative path in database
        image_path = os.path.join('uploads', filename)
    
    # Get context and notes if provided
    context = request.json.get('context')
    notes = request.json.get('notes')
    manual_mood = request.json.get('manual_mood')
    intensity = request.json.get('intensity')
    
    # Log mood in database
    mood_id = db_manager.log_mood(
        user_id=user_id,
        emotion=emotion,
        confidence=confidence,
        manual_mood=manual_mood,
        intensity=intensity,
        notes=notes,
        context=context,
        image_path=image_path
    )
    
    # Get suggestions based on detected emotion
    suggestions = suggestion_engine.get_suggestions(emotion)
    
    # Save suggestions to database
    db_manager.save_suggestions(mood_id, suggestions)
    
    # Get a personalized quote
    quote = suggestion_engine.get_personalized_quote(emotion)
    
    return jsonify({
        'emotion': emotion,
        'confidence': confidence,
        'mood_id': mood_id,
        'suggestions': suggestions,
        'quote': quote
    })

@app.route('/analytics')
@login_required
def analytics():
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get mood statistics for different time periods
    week_stats = db_manager.get_mood_stats(user_id=user_id, days=7)
    month_stats = db_manager.get_mood_stats(user_id=user_id, days=30)
    year_stats = db_manager.get_mood_stats(user_id=user_id, days=365)
    # Context averages for current month by default
    context_stats = db_manager.get_context_avg_intensity(user_id=user_id, days=30)
    
    # Get suggestion effectiveness
    suggestion_stats = db_manager.get_suggestion_effectiveness(user_id=user_id)
    
    return render_template('analytics.html',
                           week_stats=week_stats,
                           month_stats=month_stats,
                           year_stats=year_stats,
                           context_stats=context_stats,
                           suggestion_stats=suggestion_stats)

@app.route('/mood_logger')
def mood_logger():
    # Check if user is logged in
    if 'user_id' not in session:
        # For non-authenticated users, show a simplified version or redirect to login
        flash('Please log in to track your mood', 'info')
        return redirect(url_for('login', next=request.url))
    
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get recent mood
    recent_moods = db_manager.get_mood_history(user_id=user_id, limit=1)
    
    # Get mood statistics for the past week
    mood_stats = db_manager.get_mood_stats(user_id=user_id, days=7)
    
    return render_template('mood_logger.html', 
                          recent_moods=recent_moods,
                          mood_stats=mood_stats)
                          
@app.route('/save_mood', methods=['POST'])
def save_mood():
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get data from request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Extract mood data
    emotion = data.get('emotion')
    confidence_score = data.get('confidence', 0.0)  # Default to 0.0 if missing
    intensity = data.get('intensity', 5)
    notes = data.get('notes', '')
    image_data = data.get('image')
    context = data.get('context')
    
    # Validate required fields
    if not emotion:
        return jsonify({'error': 'Emotion is required'}), 400
    
    try:
        # Save image if provided
        image_path = None
        if image_data and image_data.startswith('data:image'):
            # Extract base64 data
            image_data = image_data.split(',')[1]
            # Generate unique filename
            filename = f"{uuid.uuid4()}.jpg"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save image to file
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_data))
            
            # Use relative path for database
            image_path = os.path.join('uploads', filename)
        
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert mood entry
        cursor.execute('''
            INSERT INTO moods (user_id, detected_emotion, confidence_score, intensity, notes, context, image_path, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, emotion, confidence_score, intensity, notes, context, image_path, datetime.now()))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Mood entry saved successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/mood_log')
@login_required
def mood_log():
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get all mood entries for the user
    # Default to 30 days, but allow query parameter to change the timeframe
    days = request.args.get('days', 30, type=int)
    mood_entries = db_manager.get_mood_history(user_id=user_id, days=days)
    
    return render_template('mood_log.html', mood_entries=mood_entries, days=days)

@app.route('/suggestions')
@login_required
def suggestions():
    # Get user ID from session
    user_id = session.get('user_id')
    
    # Get recent mood
    recent_moods = db_manager.get_mood_history(user_id=user_id, limit=1)
    
    if not recent_moods:
        flash('Please log your mood first to get suggestions', 'info')
        return redirect(url_for('mood_logger'))
    
    recent_mood = recent_moods[0]
    emotion = recent_mood['detected_emotion']
    
    # Get suggestions based on recent emotion
    suggestions = suggestion_engine.get_suggestions(emotion)
    
    # Get a personalized quote
    quote = suggestion_engine.get_personalized_quote(emotion)
    
    return render_template('suggestions.html',
                          emotion=emotion,
                          suggestions=suggestions,
                          quote=quote)

@app.route('/rate_suggestion', methods=['POST'])
@login_required
def rate_suggestion():
    user_id = session.get('user_id')
    suggestion_id = request.json.get('suggestion_id')
    rating = request.json.get('rating')
    
    # Save rating to database
    success = db_manager.rate_suggestion(user_id, suggestion_id, rating)
    
    return jsonify({'success': success})

@app.route('/about')
def about():
    return render_template('about.html')

# API Routes
@app.route('/api/detect-emotion', methods=['POST'])
def detect_emotion_api():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    if 'image' not in data:
        return jsonify({"error": "No image data provided"}), 400
    
    try:
        # Process the image data with the emotion detection model
        image_data = data['image']
        emotion, confidence = emotion_detector.detect_emotion_from_image(image_data)
        
        if emotion is None:
            return jsonify({
                'success': False,
                'error': 'No face detected'
            }), 400
        
        return jsonify({
            "success": True,
            "emotion": emotion,
            "confidence": confidence
        })
    except Exception as e:
        app.logger.error(f"Error in emotion detection: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)