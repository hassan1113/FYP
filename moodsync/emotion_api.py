from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import io
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import model_from_json, Sequential
import os

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)  # Enable CORS for frontend communication

# Global variables
model = None
face_cascade = None
labels = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

# Replace the load_emotion_model function with this updated version:

def load_emotion_model():
    """Load the emotion detection model"""
    global model
    try:
        app.logger.debug("Loading emotion detection model...")
        
        custom_objects = {
            'Sequential': Sequential,
            'Conv2D': tf.keras.layers.Conv2D,
            'MaxPooling2D': tf.keras.layers.MaxPooling2D,
            'Dropout': tf.keras.layers.Dropout,
            'Flatten': tf.keras.layers.Flatten,
            'Dense': tf.keras.layers.Dense
        }
        
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check multiple possible locations for model files
        possible_paths = [
            os.path.join(script_dir, "facialemotionmodel.json"),  # Current directory
            os.path.join(script_dir, "models", "facialemotionmodel.json"),  # models subdirectory
        ]
        
        json_path = None
        h5_path = None
        
        # Find the JSON file
        for path in possible_paths:
            if os.path.exists(path):
                json_path = path
                h5_path = path.replace(".json", ".h5")
                app.logger.debug(f"Found JSON file at: {json_path}")
                break
        
        if not json_path or not os.path.exists(json_path):
            app.logger.warning(f"Model JSON file not found in any location")
            app.logger.debug(f"Checked paths: {possible_paths}")
            return False
        
        if not os.path.exists(h5_path):
            app.logger.warning(f"Model H5 file not found at: {h5_path}")
            return False
            
        app.logger.debug(f"Using JSON path: {json_path}")
        app.logger.debug(f"Using H5 path: {h5_path}")
        
        with open(json_path, "r") as json_file:
            model_json = json_file.read()
            
        model = model_from_json(model_json, custom_objects=custom_objects)
        model.load_weights(h5_path)
        app.logger.info("Emotion detection model loaded successfully!")
        return True
        
    except Exception as e:
        app.logger.error(f"Error loading model: {e}")
        model = None
        return False

def initialize_face_detection():
    """Initialize face detection cascade"""
    global face_cascade
    try:
        haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(haar_file)
        
        if face_cascade.empty():
            print("Error: Could not load face detection cascade")
            return False
            
        print("Face detection initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing face detection: {e}")
        return False

def extract_features(image):
    """Extract features from face image for emotion prediction"""
    if image is None or image.size == 0:
        app.logger.warning("Empty image provided for feature extraction")
        return None
    
    app.logger.debug(f"Extracting features from image with shape: {image.shape}")
    
    try:
        # Preprocess image
        image = cv2.equalizeHist(image)
        image = cv2.resize(image, (48, 48))
        feature = np.array(image, dtype=np.float32)
        feature = feature.reshape(1, 48, 48, 1)
        return feature / 255.0
    except Exception as e:
        app.logger.error(f"Error in extract_features: {e}")
        return None

def detect_faces_and_emotions(image_array):
    """Detect faces and predict emotions"""
    try:
        app.logger.debug("Detecting faces and emotions...")
        
        # Convert to grayscale if it's a color image
        if len(image_array.shape) == 3:
            if image_array.shape[2] == 4:  # RGBA image
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGBA2GRAY)
            elif image_array.shape[2] == 3:  # RGB image
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                app.logger.error(f"Unexpected number of channels: {image_array.shape[2]}")
                return {'success': False, 'error': f'Unsupported image format with {image_array.shape[2]} channels'}
        else:
            # Already grayscale
            gray = image_array
        
        app.logger.debug(f"Image shape: {image_array.shape}, Grayscale shape: {gray.shape}")
        
        # Apply Gaussian blur
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            maxSize=(300, 300)
        )
        
        app.logger.debug(f"Detected {len(faces)} faces in the image")
        
        if len(faces) == 0:
            return {'success': False, 'error': 'No faces detected in the image'}
        
        # Process the first detected face
        x, y, w, h = faces[0]
        app.logger.debug(f"Processing face at coordinates: x={x}, y={y}, w={w}, h={h}")
        
        # Extract face region with padding
        padding = 10
        face_region = gray[max(0, y-padding):min(gray.shape[0], y+h+padding),
                          max(0, x-padding):min(gray.shape[1], x+w+padding)]
        
        if face_region.size == 0:
            return {'success': False, 'error': 'Invalid face region extracted'}
        
        # Extract features and predict emotion
        features = extract_features(face_region)
        
        if features is None or model is None:
            return {'success': False, 'error': 'Feature extraction failed or model not available'}
        
        # Make prediction
        prediction = model.predict(features, verbose=0)
        confidence = float(np.max(prediction))
        emotion_index = int(np.argmax(prediction))
        emotion = labels[emotion_index]
        
        app.logger.debug(f"Prediction: {emotion} with confidence {confidence}")
        
        # Only return result if confidence is reasonable
        if confidence < 0.3:
            return {'success': False, 'error': 'Low confidence prediction', 'confidence': confidence}
        
        return {
            'success': True,
            'emotion': emotion,
            'confidence': confidence,
            'all_predictions': {labels[i]: float(prediction[0][i]) for i in range(len(labels))},
            'face_coordinates': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)}
        }
        
    except Exception as e:
        app.logger.error(f"Error in emotion detection: {e}")
        return {'success': False, 'error': f'Detection error: {str(e)}'}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'face_detection_ready': face_cascade is not None and not face_cascade.empty()
    })

@app.route('/api/detect-emotion', methods=['POST'])
def detect_emotion():
    """Main emotion detection endpoint"""
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({
                'success': False, 
                'error': 'Emotion detection model is not available. Please check model files.'
            }), 500
        
        # Check if face detection is ready
        if face_cascade is None or face_cascade.empty():
            return jsonify({
                'success': False, 
                'error': 'Face detection is not available.'
            }), 500
        
        # Get image from request
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({'success': False, 'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image']
        
        # Remove data URL prefix if present
        if image_data.startswith('data:image'):
            image_data = image_data.split(',')[1]
            
        # ADD THIS DEBUG LINE
        print(f"Received image data length: {len(image_data)}")
        
        # Decode base64 to image
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Detect faces and emotions
        result = detect_faces_and_emotions(image_array)
        
        # ADD THIS DEBUG LINE (after getting the result)
        if result.get('success'):
            print(f"Prediction result: {result['emotion']} with confidence {result['confidence']}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            'success': False, 
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/emotions/list', methods=['GET'])
def list_emotions():
    """Get list of supported emotions"""
    return jsonify({
        'emotions': list(labels.values()),
        'labels': labels
    })

# Add this route to your emotion_api.py file:

@app.route('/')
def home():
    return jsonify({
        'message': 'Emotion Detection API is running',
        'endpoints': {
            'health': '/api/health',
            'detect_emotion': '/api/detect-emotion (POST)',
            'emotions_list': '/api/emotions/list'
        },
        'status': {
            'model_loaded': model is not None,
            'face_detection_ready': face_cascade is not None and not face_cascade.empty()
        }
    })

# Debug: Print all registered routes
print("=== REGISTERED ROUTES ===")
for rule in app.url_map.iter_rules():
    print(f"  {rule.rule} -> {rule.endpoint}")
print("========================")

# Also add route debugging
@app.before_request
def log_request_info():
    print(f"Request: {request.method} {request.url}")

if __name__ == '__main__':
    print("Initializing Emotion Detection API...")
    
    # Initialize components
    model_loaded = load_emotion_model()
    face_detection_ready = initialize_face_detection()
    
    if not model_loaded:
        print("Warning: Running without emotion detection model")
    
    if not face_detection_ready:
        print("Warning: Running without face detection")
    
    print("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True)