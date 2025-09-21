import os

class Config:
    # Flask configuration
    SECRET_KEY = 'your-secret-key-here'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # Database configuration
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database/moodsync.db')
    
    # Model configuration
    MODEL_JSON_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'facialemotionmodel.json')
    MODEL_H5_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'facialemotionmodel.h5')
    
    # Allowed image extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    
    # Emotion labels
    EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']