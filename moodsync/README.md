# MoodSync - Emotion Detection and Mood Tracking Application

MoodSync is a web application that uses computer vision and machine learning to detect emotions from facial expressions, track mood patterns over time, and provide personalized suggestions based on emotional states.

## Features

- **Real-time Emotion Detection**: Capture your facial expression using a webcam and automatically detect your current emotional state
- **Mood Tracking**: Log your emotions with context information and track patterns over time
- **Personalized Suggestions**: Receive tailored recommendations based on your emotional state
- **Analytics Dashboard**: Visualize your mood trends, emotion distribution, and suggestion effectiveness
- **User Profiles**: Customize your experience with personalized settings

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Machine Learning**: TensorFlow/Keras for emotion detection
- **Data Visualization**: Chart.js
- **Database**: SQLite

## Project Structure

```
moodsync/
├── app.py                  # Main Flask application
├── config.py               # Configuration settings
├── models/
│   ├── emotion_detector.py # Emotion detection using ML model
│   ├── ai_suggestions.py   # Suggestion engine
│   └── database.py         # Database operations
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── images/             # Image assets
├── templates/              # HTML templates
└── database/              # SQLite database files
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Pip package manager
- Webcam (for emotion detection)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/moodsync.git
   cd moodsync
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download the pre-trained emotion detection model (if not included):
   - Place the model files in the appropriate directory as specified in config.py
   - Alternatively, you can train your own model using the provided scripts

5. Initialize the database:
   ```
   python -c "from moodsync.models.database import DatabaseManager; DatabaseManager().init_db()"
   ```

### Running the Application

1. Start the Flask development server:
   ```
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Usage Guide

### Logging Your Mood

1. Navigate to the "Log Mood" page
2. Allow camera access when prompted
3. Click the "Capture" button to take a photo
4. Click "Detect Emotion" to analyze your facial expression
5. Add additional context information (optional)
6. Submit to save your mood entry

### Viewing Analytics

1. Navigate to the "Analytics" page
2. View your mood trends over time
3. Analyze emotion distribution and patterns
4. See which suggestions have been most effective

### Getting Suggestions

1. After logging your mood, you'll be redirected to the suggestions page
2. Rate suggestions to help improve future recommendations
3. Access the suggestions page anytime from the dashboard

## Customization

### Appearance

- Toggle between light and dark mode in the settings
- Customize dashboard layout preferences

### Notifications

- Enable or disable mood logging reminders
- Set custom reminder schedules

## Privacy

MoodSync is designed with privacy in mind:

- All data is stored locally on your device
- Captured images are processed locally and not sent to external servers
- You can delete your data at any time through the settings page

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Emotion detection model based on research by [citation]
- Icons provided by Bootstrap Icons
- Chart visualizations powered by Chart.js