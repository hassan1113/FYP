import cv2
import numpy as np
from tensorflow.keras.models import load_model, model_from_json
from PIL import Image
import base64
import io
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class EmotionDetector:
    def __init__(self):
        try:
            # Load model architecture from JSON file
            json_file = open(Config.MODEL_JSON_PATH, "r")
            model_json = json_file.read()
            json_file.close()
            
            # Register custom objects to ensure compatibility
            from tensorflow.keras.models import Sequential
            from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
            
            custom_objects = {
                'Sequential': Sequential,
                'Conv2D': Conv2D,
                'MaxPooling2D': MaxPooling2D,
                'Dropout': Dropout,
                'Flatten': Flatten,
                'Dense': Dense
            }
            
            # Create model from JSON and load weights
            self.model = model_from_json(model_json, custom_objects=custom_objects)
            self.model.load_weights(Config.MODEL_H5_PATH)
            print("Model loaded successfully!")
            
            # Initialize face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.emotion_labels = Config.EMOTION_LABELS
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def detect_emotion_from_image(self, image_data):
        # Convert base64 to image
        image = self.base64_to_image(image_data)
        
        # Apply horizontal flip to correct the mirroring effect
        image = cv2.flip(image, 1)
        
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
        # Remove header if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Convert base64 to image
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to numpy array for OpenCV processing
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    def detect_faces(self, image):
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces with improved parameters
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        return faces
    
    def extract_face(self, image, face_coords):
        x, y, w, h = face_coords
        
        # Extract face region
        face_img = image[y:y+h, x:x+w]
        
        # Resize to model input size (48x48)
        face_img = cv2.resize(face_img, (48, 48))
        
        # Convert to grayscale
        face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
        
        # Normalize pixel values
        face_img = face_img / 255.0
        
        # Reshape for model input
        face_img = np.reshape(face_img, (1, 48, 48, 1))
        
        return face_img
    
    def detect_emotion_from_frame(self, frame):
        # Detect faces
        faces = self.detect_faces(frame)
        
        results = []
        for (x, y, w, h) in faces:
            # Extract and process face
            face = self.extract_face(frame, (x, y, w, h))
            
            # Predict emotion
            emotion_probs = self.model.predict(face)
            emotion_index = np.argmax(emotion_probs)
            confidence = emotion_probs[0][emotion_index]
            emotion = self.emotion_labels[emotion_index]
            
            results.append({
                'coords': (x, y, w, h),
                'emotion': emotion,
                'confidence': float(confidence)
            })
        
        return results