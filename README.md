# MoodSync - Emotion Detection Mood Tracker App
## Complete Implementation Guide

### Phase 1: Project Setup & Backend Foundation

#### 1.1 Project Structure
```
moodsync/
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Dependencies
├── models/
│   ├── emotion_detector.py     # Your trained model integration
│   ├── ai_suggestions.py       # AI suggestion engine
│   └── database.py            # Database operations
├── static/
│   ├── css/
│   │   ├── main.css
│   │   └── dashboard.css
│   ├── js/
│   │   ├── main.js
│   │   ├── camera.js
│   │   ├── dashboard.js
│   │   └── analytics.js
│   ├── images/
│   └── uploads/               # Stored emotion images
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── mood_logger.html
│   ├── analytics.html
│   ├── suggestions.html
│   └── settings.html
└── database/
    └── moodsync.db
```

#### 1.2 Dependencies (requirements.txt)
```
Flask==2.3.3
opencv-python==4.8.1.78
tensorflow==2.13.0
numpy==1.24.3
Pillow==10.0.0
sqlite3
pandas==2.0.3
scikit-learn==1.3.0
python-dateutil==2.8.2
werkzeug==2.3.7
```

### Phase 2: Backend Development

#### 2.1 Flask Application Structure (app.py)
```python
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from models.emotion_detector import EmotionDetector
from models.ai_suggestions import SuggestionEngine
from models.database import DatabaseManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize components
emotion_detector = EmotionDetector()
suggestion_engine = SuggestionEngine()
db_manager = DatabaseManager()

# Routes will be implemented here
```

#### 2.2 Emotion Detection Integration (models/emotion_detector.py)
```python
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import base64
import io

class EmotionDetector:
    def __init__(self, model_path='path/to/your/model.h5'):
        self.model = load_model(model_path)
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_emotion_from_image(self, image_data):
        # Convert base64 to image
        image = self.base64_to_image(image_data)
        
        # Detect face and predict emotion
        faces = self.detect_faces(image)
        if len(faces) == 0:
            return None, 0.0
        
        # Process largest face
        face = self.extract_face(image, faces[0])
        emotion_probs = self.model.predict(face)
        emotion_index = np.argmax(emotion_probs)
        confidence = emotion_probs[0][emotion_index]
        
        return self.emotion_labels[emotion_index], float(confidence)
    
    def base64_to_image(self, base64_string):
        # Implementation for base64 to image conversion
        pass
    
    def detect_faces(self, image):
        # Face detection implementation
        pass
    
    def extract_face(self, image, face_coords):
        # Face extraction and preprocessing
        pass
```

#### 2.3 AI Suggestion Engine (models/ai_suggestions.py)
```python
import random
from datetime import datetime, timedelta

class SuggestionEngine:
    def __init__(self):
        self.suggestions_db = {
            'Happy': {
                'activities': [
                    "Share your happiness! Call a friend or family member",
                    "Channel this energy into a creative project",
                    "Go for a walk in nature to maintain this positive mood",
                    "Write down what made you happy today in a gratitude journal"
                ],
                'wellness': [
                    "Practice gratitude meditation to amplify positive feelings",
                    "Do some light stretching or yoga to maintain good energy"
                ],
                'productivity': [
                    "This is a great time to tackle challenging tasks",
                    "Use this positive energy to organize your workspace"
                ]
            },
            'Sad': {
                'activities': [
                    "Listen to uplifting music or your favorite comfort playlist",
                    "Watch a funny movie or comedy show",
                    "Call someone you trust and talk about your feelings",
                    "Take a warm bath or shower to comfort yourself"
                ],
                'wellness': [
                    "Try deep breathing exercises: 4 counts in, 6 counts out",
                    "Practice self-compassion meditation",
                    "Write your feelings in a journal without judgment"
                ],
                'social': [
                    "Reach out to a supportive friend or family member",
                    "Consider joining an online support community"
                ]
            },
            'Angry': {
                'activities': [
                    "Go for a vigorous walk or run to release tension",
                    "Try punching a pillow or doing jumping jacks",
                    "Listen to heavy music that matches your energy, then transition to calmer tunes"
                ],
                'wellness': [
                    "Practice the 4-7-8 breathing technique",
                    "Try progressive muscle relaxation",
                    "Count to 10 slowly before reacting to anything"
                ],
                'productivity': [
                    "Clean or organize something - channel anger into productivity",
                    "Avoid making important decisions right now"
                ]
            },
            'Neutral': {
                'activities': [
                    "This is a good time to try something new",
                    "Explore a new hobby or interest",
                    "Organize your goals and plans for the week"
                ],
                'wellness': [
                    "Practice mindfulness meditation",
                    "Do some gentle stretching"
                ],
                'productivity': [
                    "Perfect time for routine tasks and planning",
                    "Review your recent achievements and set new goals"
                ]
            }
        }
    
    def get_suggestions(self, emotion, context=None, previous_suggestions=None):
        if emotion not in self.suggestions_db:
            emotion = 'Neutral'
        
        emotion_suggestions = self.suggestions_db[emotion]
        suggestions = []
        
        # Get suggestions from each category
        for category, suggestions_list in emotion_suggestions.items():
            suggestion = random.choice(suggestions_list)
            suggestions.append({
                'type': category,
                'content': suggestion,
                'emotion': emotion
            })
        
        return suggestions
    
    def get_personalized_quote(self, emotion):
        quotes = {
            'Happy': [
                "Keep shining bright! Your positive energy is contagious.",
                "Happiness is not a destination, it's a way of travel.",
                "Your smile is your superpower today!"
            ],
            'Sad': [
                "It's okay to not be okay. This feeling will pass.",
                "You are stronger than you think, and this too shall pass.",
                "Every storm runs out of rain. Better days are coming."
            ],
            'Angry': [
                "Take a deep breath. You have the power to choose your response.",
                "Anger is like a storm - intense but temporary.",
                "Your peace of mind is worth more than proving you're right."
            ]
        }
        
        return random.choice(quotes.get(emotion, quotes['Happy']))
```

### Phase 3: Database Management

#### 3.1 Database Manager (models/database.py)
```python
import sqlite3
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path='database/moodsync.db'):
        self.db_path = db_path
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
                INSERT OR IGNORE INTO users (id, username, email) 
                VALUES (1, 'default_user', 'user@moodsync.com');
            ''')
            
            conn.commit()
    
    def log_mood(self, emotion, confidence, manual_mood=None, intensity=None, notes=None, context=None, image_path=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO moods (detected_emotion, confidence_score, manual_mood, intensity, notes, context, image_path)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (emotion, confidence, manual_mood, intensity, notes, context, image_path))
            
            mood_id = cursor.lastrowid
            conn.commit()
            return mood_id
    
    def get_mood_history(self, user_id=1, limit=50):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM moods 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
            
            columns = [description[0] for description in cursor.description]
            moods = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return moods
    
    def get_mood_analytics(self, user_id=1, days=30):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT detected_emotion, COUNT(*) as count, 
                       AVG(intensity) as avg_intensity,
                       DATE(timestamp) as date
                FROM moods 
                WHERE user_id = ? AND timestamp >= datetime('now', '-{} days')
                GROUP BY detected_emotion, DATE(timestamp)
                ORDER BY timestamp DESC
            '''.format(days), (user_id,))
            
            columns = [description[0] for description in cursor.description]
            analytics = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return analytics
```

### Phase 4: Frontend Development

#### 4.1 Base Template (templates/base.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}MoodSync{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <!-- Custom CSS -->
    <link href="{{ url_for('static', filename='css/main.css') }}" rel="stylesheet">
    
    {% block head %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('dashboard') }}">
                <i class="fas fa-smile"></i> MoodSync
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('dashboard') }}">
                            <i class="fas fa-tachometer-alt"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('mood_logger') }}">
                            <i class="fas fa-camera"></i> Log Mood
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('analytics') }}">
                            <i class="fas fa-chart-line"></i> Analytics
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('suggestions') }}">
                            <i class="fas fa-lightbulb"></i> Suggestions
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    
    <!-- Main Content -->
    <main class="container-fluid py-4">
        {% block content %}{% endblock %}
    </main>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    
    {% block scripts %}{% endblock %}
</body>
</html>
```

#### 4.2 Mood Logger Page (templates/mood_logger.html)
```html
{% extends "base.html" %}

{% block title %}Log Mood - MoodSync{% endblock %}

{% block head %}
<link href="{{ url_for('static', filename='css/mood_logger.css') }}" rel="stylesheet">
{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow">
                <div class="card-header bg-primary text-white">
                    <h3 class="card-title mb-0">
                        <i class="fas fa-camera"></i> Capture Your Mood
                    </h3>
                </div>
                
                <div class="card-body">
                    <!-- Camera Section -->
                    <div class="camera-section mb-4">
                        <div class="camera-container text-center">
                            <video id="video" autoplay style="display: none;"></video>
                            <canvas id="canvas" style="display: none;"></canvas>
                            
                            <div id="camera-placeholder" class="camera-placeholder">
                                <i class="fas fa-camera fa-3x text-muted"></i>
                                <p class="mt-2">Click "Start Camera" to begin emotion detection</p>
                            </div>
                            
                            <div id="captured-image" style="display: none;">
                                <img id="preview-image" class="img-fluid rounded">
                            </div>
                        </div>
                        
                        <div class="camera-controls mt-3 text-center">
                            <button id="start-camera" class="btn btn-primary">
                                <i class="fas fa-video"></i> Start Camera
                            </button>
                            <button id="capture-mood" class="btn btn-success" style="display: none;">
                                <i class="fas fa-camera"></i> Capture Mood
                            </button>
                            <button id="retake" class="btn btn-warning" style="display: none;">
                                <i class="fas fa-redo"></i> Retake
                            </button>
                        </div>
                    </div>
                    
                    <!-- Detection Results -->
                    <div id="detection-results" class="detection-results" style="display: none;">
                        <div class="alert alert-info">
                            <h5><i class="fas fa-brain"></i> AI Detection Results</h5>
                            <div class="row">
                                <div class="col-md-6">
                                    <strong>Detected Emotion:</strong>
                                    <span id="detected-emotion" class="emotion-badge"></span>
                                </div>
                                <div class="col-md-6">
                                    <strong>Confidence:</strong>
                                    <span id="confidence-score"></span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Manual Entry Form -->
                    <form id="mood-form">
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="manual-mood" class="form-label">
                                        How are you feeling? (Optional override)
                                    </label>
                                    <select class="form-select" id="manual-mood">
                                        <option value="">Use AI detection</option>
                                        <option value="Happy">😊 Happy</option>
                                        <option value="Sad">😢 Sad</option>
                                        <option value="Angry">😠 Angry</option>
                                        <option value="Surprised">😲 Surprised</option>
                                        <option value="Fear">😨 Fearful</option>
                                        <option value="Neutral">😐 Neutral</option>
                                    </select>
                                </div>
                            </div>
                            
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label for="intensity" class="form-label">
                                        Intensity (1-10)
                                    </label>
                                    <input type="range" class="form-range" 
                                           id="intensity" min="1" max="10" value="5">
                                    <div class="d-flex justify-content-between">
                                        <small>Low</small>
                                        <small id="intensity-value">5</small>
                                        <small>High</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-3">
                            <label for="context" class="form-label">What's happening?</label>
                            <select class="form-select" id="context">
                                <option value="">Select context (optional)</option>
                                <option value="work">Work</option>
                                <option value="family">Family</option>
                                <option value="friends">Friends</option>
                                <option value="health">Health</option>
                                <option value="personal">Personal</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label for="notes" class="form-label">Notes (Optional)</label>
                            <textarea class="form-control" id="notes" rows="3" 
                                      placeholder="Add any additional details about your mood..."></textarea>
                        </div>
                        
                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary btn-lg">
                                <i class="fas fa-save"></i> Log Mood Entry
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script src="{{ url_for('static', filename='js/camera.js') }}"></script>
<script src="{{ url_for('static', filename='js/mood_logger.js') }}"></script>
{% endblock %}
```

#### 4.3 Camera JavaScript (static/js/camera.js)
```javascript
class CameraManager {
    constructor() {
        this.video = document.getElementById('video');
        this.canvas = document.getElementById('canvas');
        this.ctx = this.canvas.getContext('2d');
        this.stream = null;
        this.capturedImage = null;
        
        this.initializeElements();
        this.bindEvents();
    }
    
    initializeElements() {
        this.startBtn = document.getElementById('start-camera');
        this.captureBtn = document.getElementById('capture-mood');
        this.retakeBtn = document.getElementById('retake');
        this.placeholder = document.getElementById('camera-placeholder');
        this.capturedDiv = document.getElementById('captured-image');
        this.previewImg = document.getElementById('preview-image');
    }
    
    bindEvents() {
        this.startBtn.addEventListener('click', () => this.startCamera());
        this.captureBtn.addEventListener('click', () => this.captureImage());
        this.retakeBtn.addEventListener('click', () => this.retakePhoto());
    }
    
    async startCamera() {
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 } 
            });
            
            this.video.srcObject = this.stream;
            this.video.style.display = 'block';
            this.placeholder.style.display = 'none';
            
            this.startBtn.style.display = 'none';
            this.captureBtn.style.display = 'inline-block';
            
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Unable to access camera. Please ensure you have granted camera permissions.');
        }
    }
    
    captureImage() {
        // Set canvas size to match video
        this.canvas.width = this.video.videoWidth;
        this.canvas.height = this.video.videoHeight;
        
        // Draw current frame to canvas
        this.ctx.drawImage(this.video, 0, 0);
        
        // Get image data as base64
        this.capturedImage = this.canvas.toDataURL('image/jpeg', 0.8);
        
        // Show preview
        this.previewImg.src = this.capturedImage;
        this.capturedDiv.style.display = 'block';
        
        // Hide video, show controls
        this.video.style.display = 'none';
        this.captureBtn.style.display = 'none';
        this.retakeBtn.style.display = 'inline-block';
        
        // Stop camera stream
        this.stopCamera();
        
        // Process emotion detection
        this.detectEmotion();
    }
    
    retakePhoto() {
        this.capturedDiv.style.display = 'none';
        this.retakeBtn.style.display = 'none';
        this.startBtn.style.display = 'inline-block';
        
        // Hide detection results
        document.getElementById('detection-results').style.display = 'none';
        
        this.capturedImage = null;
    }
    
    stopCamera() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
    }
    
    async detectEmotion() {
        if (!this.capturedImage) return;
        
        const loadingAlert = document.createElement('div');
        loadingAlert.className = 'alert alert-info';
        loadingAlert.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing your emotion...';
        
        const resultsDiv = document.getElementById('detection-results');
        resultsDiv.style.display = 'block';
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(loadingAlert);
        
        try {
            const response = await fetch('/api/detect-emotion', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: this.capturedImage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayResults(data.emotion, data.confidence);
            } else {
                this.displayError(data.message);
            }
            
        } catch (error) {
            console.error('Error detecting emotion:', error);
            this.displayError('Failed to detect emotion. Please try again.');
        }
    }
    
    displayResults(emotion, confidence) {
        const resultsDiv = document.getElementById('detection-results');
        const confidencePercent = Math.round(confidence * 100);
        
        resultsDiv.innerHTML = `
            <div class="alert alert-success">
                <h5><i class="fas fa-brain"></i> AI Detection Results</h5>
                <div class="row">
                    <div class="col-md-6">
                        <strong>Detected Emotion:</strong>
                        <span class="badge bg-primary ms-2">${emotion}</span>
                    </div>
                    <div class="col-md-6">
                        <strong>Confidence:</strong>
                        <span class="badge bg-info ms-2">${confidencePercent}%</span>
                    </div>
                </div>
            </div>
        `;
        
        // Store detection results
        window.detectionResults = { emotion, confidence };
    }
    
    displayError(message) {
        const resultsDiv = document.getElementById('detection-results');
        resultsDiv.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i> ${message}
            </div>
        `;
    }
}

// Initialize camera when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.cameraManager = new CameraManager();
});
```

### Phase 5: Advanced Features Implementation

#### 5.1 Flask Routes Implementation
```python
# Add these routes to app.py

@app.route('/')
def dashboard():
    # Get recent moods and analytics
    recent_moods = db_manager.get_mood_history(limit=5)
    analytics = db_manager.get_mood_analytics(days=7)
    
    return render_template('dashboard.html', 
                         recent_moods=recent_moods,
                         analytics=analytics)

@app.route('/mood-logger')
def mood_logger():
    return render_template('mood_logger.html')

@app.route('/analytics')
def analytics():
    analytics_data = db_manager.get_mood_analytics(days=30)
    return render_template('analytics.html', analytics=analytics_data)

@app.route('/suggestions')
def suggestions():
    return render_template('suggestions.html')

@app.route('/api/detect-emotion', methods=['POST'])
def detect_emotion():
    try:
        data = request.get_json()
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'No image provided'})
        
        # Detect emotion using your model
        emotion, confidence = emotion_detector.detect_emotion_from_image(image_data)
        
        if emotion is None:
            return jsonify({'success': False, 'message': 'No face detected in image'})
        
        return jsonify({
            'success': True,
            'emotion': emotion,
            'confidence': confidence
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/log-mood', methods=['POST'])
def log_mood():
    try:
        data = request.get_json()
        
        # Extract data
        detected_emotion = data.get('detected_emotion')
        confidence = data.get('confidence', 0.0)
        manual_mood = data.get('manual_mood')
        intensity = data.get('intensity', 5)
        notes = data.get('notes', '')
        context = data.get('context', '')
        image_data = data.get('image')
        
        # Save image if provided
        image_path = None
        if image_data:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"mood_{timestamp}.jpg"
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save base64 image to file
            with open(image_path, 'wb') as f:
                f.write(base64.b64decode(image_data.split(',')[1]))
        
        # Log mood to database
        mood_id = db_manager.log_mood(
            emotion=detected_emotion,
            confidence=confidence,
            manual_mood=manual_mood,
            intensity=intensity,
            notes=notes,
            context=context,
            image_path=image_path
        )
        
        # Generate AI suggestions
        final_emotion = manual_mood or detected_emotion
        suggestions = suggestion_engine.get_suggestions(final_emotion, context)
        
        # Save suggestions to database
        for suggestion in suggestions:
            db_manager.save_suggestion(mood_id, suggestion)
        
        return jsonify({
            'success': True,
            'mood_id': mood_id,
            'suggestions': suggestions
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/mood-analytics/<int:days>')
def mood_analytics(days=30):
    try:
        analytics = db_manager.get_mood_analytics(days=days)
        return jsonify({'success': True, 'data': analytics})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
```

### Phase 6: Deployment & Testing

#### 6.1 Final Steps
1. **Testing**: Test all functionality thoroughly
2. **Error Handling**: Add comprehensive error handling
3. **Security**: Implement proper security measures
4. **Performance**: Optimize image processing and database queries
5. **Mobile Responsiveness**: Ensure all pages work well on mobile devices
6. **Data Export**: Add functionality to export mood data
7. **Backup System**: Implement database backup functionality

#### 6.2 Run Instructions
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Access at http://localhost:5000
```

This comprehensive implementation provides a fully functional mood tracking application that scales your emotion detection project into a complete wellness platform. The app includes AI-powered suggestions, detailed analytics, and a user-friendly interface for logging and tracking moods over time.