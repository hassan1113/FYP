# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Quick Start Commands

### Installing Dependencies
```powershell
# Main project dependencies (root directory)
pip install -r requirements.txt

# MoodSync web app dependencies (from moodsync/ subdirectory)
pip install -r moodsync/requirements.txt
```

### Running the Applications
```powershell
# Real-time emotion detection with webcam
python liveemotiondetector.py

# MoodSync web application (Flask app)
cd moodsync
python app.py
# Access at: http://localhost:4000

# Emotion detection API server
cd moodsync
python emotion_api.py
# API available at: http://localhost:5000

# Jupyter notebook for model training/analysis
jupyter notebook Emotion_Detection.ipynb
```

### Testing & Development
```powershell
# Test image analysis
python analyze_image.py

# Check model loading and basic functionality
cd moodsync
python -c "from models.emotion_detector import EmotionDetector; ed = EmotionDetector(); print('Model loaded successfully' if ed.model else 'Model failed to load')"
```

## Project Architecture

### High-Level Structure
This is a multi-component emotion detection system with three main layers:

1. **Core ML Layer**: TensorFlow/Keras CNN model for emotion classification (7 emotions: Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise)
2. **Application Layer**: Flask web applications and APIs for user interaction
3. **Data Layer**: SQLite database with user management, mood tracking, and AI suggestions

### Component Interaction Flow
```
Raw Image/Video → Face Detection (OpenCV Haar Cascades) → Face Preprocessing (48x48 grayscale) → 
CNN Model Prediction → Emotion Classification → AI Suggestion Engine → Database Storage → Web Interface
```

### Key Components

#### Model Architecture (`facialemotionmodel.h5/.json`)
- Input: 48x48 grayscale facial images
- CNN with Conv2D, MaxPooling2D, Dropout, and Dense layers
- Output: 7-class emotion probabilities
- Located in `moodsync/` directory

#### MoodSync Web Application (`moodsync/`)
**Core Files:**
- `app.py`: Main Flask application with user authentication, mood logging, and dashboard
- `emotion_api.py`: Standalone API server for emotion detection services
- `config.py`: Centralized configuration including model paths and database settings

**Model Classes (`moodsync/models/`):**
- `emotion_detector.py`: Handles model loading, face detection, and emotion prediction
- `database.py`: SQLite operations for users, moods, and suggestions with analytics queries
- `ai_suggestions.py`: Context-aware suggestion engine with emotion-specific recommendations

#### Real-time Detection (`liveemotiondetector.py`)
- Direct webcam integration with OpenCV
- Real-time face detection and emotion classification
- Interactive wellness suggestions with keyboard controls
- Multi-face detection capability

### Database Schema
- **users**: User authentication and profiles
- **moods**: Emotion logs with confidence scores, manual overrides, context, and timestamps
- **suggestions**: AI-generated recommendations with effectiveness ratings

### Important Architectural Notes

#### Model Loading Pattern
The system uses a robust model loading approach with custom TensorFlow objects registration to ensure compatibility across different TensorFlow versions. All three components (`liveemotiondetector.py`, `emotion_detector.py`, `emotion_api.py`) implement similar model loading with error handling.

#### Face Detection Strategy
Uses OpenCV Haar Cascades with optimized parameters:
- Primary: `haarcascade_frontalface_default.xml`
- Backup: `haarcascade_profileface.xml` (in live detector)
- Face preprocessing: resize to 48x48, grayscale conversion, normalization

#### API Design
The emotion detection API follows RESTful patterns:
- `POST /api/detect-emotion`: Accepts base64 image data
- `GET /api/health`: System health check
- `GET /api/emotions/list`: Supported emotion categories

#### Session Management
Flask app uses session-based authentication with configurable session lifetime and "remember me" functionality.

### Development Patterns

#### Error Handling
- Model loading failures are gracefully handled with detailed logging
- Face detection failures return appropriate error responses
- Database operations use proper exception handling with rollback capabilities

#### Configuration Management
Centralized configuration in `config.py` with environment-aware paths and settings. Model paths are resolved dynamically based on script location.

#### Data Flow
1. Image capture (webcam/upload) → Base64 encoding
2. Face detection → Region extraction with padding
3. Preprocessing → 48x48 grayscale normalization
4. Model inference → Confidence scoring
5. Suggestion generation → Database persistence
6. Analytics computation → Dashboard visualization

## Common Development Tasks

### Adding New Emotions
1. Update `EMOTION_LABELS` in `config.py`
2. Retrain model with new classes
3. Add suggestions in `ai_suggestions.py`
4. Update label mappings in `emotion_api.py`

### Model Updates
1. Replace `facialemotionmodel.h5` and `facialemotionmodel.json` in `moodsync/`
2. Verify model loading across all components
3. Test face detection and preprocessing pipeline
4. Update emotion labels if classification changed

### Database Schema Changes
1. Modify `init_database()` in `database.py`
2. Add migration logic for existing data
3. Update analytics queries as needed
4. Test with both SQLite file and in-memory databases

### API Extensions
1. Add new routes in `emotion_api.py`
2. Update CORS settings if needed
3. Add corresponding frontend integration
4. Document new endpoints

## File Organization

- **Root**: Core detection scripts and Jupyter notebook
- **moodsync/**: Complete web application with MVC structure
- **moodsync/models/**: Business logic classes
- **moodsync/templates/**: HTML templates (mentioned in README)
- **moodsync/static/**: CSS, JavaScript, and image assets
- **moodsync/database/**: SQLite database files
- **images/**: Training and test datasets for model development

This architecture supports both real-time detection and web-based mood tracking with a clean separation between ML inference, business logic, and user interface layers.