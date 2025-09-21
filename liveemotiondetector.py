import cv2
import numpy as np
import random
import time
import threading
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import Sequential
import os

# Load model
# Initialize model as None first
model = None

try:
    # Register custom objects to ensure compatibility
    custom_objects = {
        'Sequential': Sequential,
        'Conv2D': tf.keras.layers.Conv2D,
        'MaxPooling2D': tf.keras.layers.MaxPooling2D,
        'Dropout': tf.keras.layers.Dropout,
        'Flatten': tf.keras.layers.Flatten,
        'Dense': tf.keras.layers.Dense
    }
    
    model_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(model_dir, "moodsync", "facialemotionmodel.json")
    h5_path = os.path.join(model_dir, "moodsync", "facialemotionmodel.h5")
    
    # Check if model files exist
    if not os.path.exists(json_path) or not os.path.exists(h5_path):
        print(f"Error: Model files not found at {model_dir}")
        print(f"JSON file exists: {os.path.exists(json_path)}")
        print(f"H5 file exists: {os.path.exists(h5_path)}")
    else:
        json_file = open(json_path, "r")
        model_json = json_file.read()
        json_file.close()
        model = model_from_json(model_json, custom_objects=custom_objects)
        model.load_weights(h5_path)
        print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Initialize face detection with improved parameters
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)
profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')

# Emotion-based responses
emotion_responses = {
   'Angry': {
       'quotes': [
           "Take a deep breath. This too shall pass.",
           "Anger is one letter short of danger. Stay calm.",
           "You have power over your mind - not events. Realize this.",
           "The best revenge is massive success.",
           "Peace cannot be kept by force; it can only be achieved by understanding."
       ],
       'activities': [
           "Try deep breathing: Inhale for 4, hold for 4, exhale for 4",
           "Take a 5-minute walk outside",
           "Listen to calming music",
           "Practice progressive muscle relaxation",
           "Write down your thoughts in a journal"
       ],
       'tasks': [
           "Count backwards from 100 by 7s",
           "Name 5 things you can see, 4 you can touch, 3 you can hear",
           "Do 10 push-ups to release tension",
           "Call a friend or family member",
           "Practice gratitude: list 3 things you're thankful for"
       ]
   },
   'Sad': {
       'quotes': [
           "Every storm runs out of rain. You will smile again.",
           "The sun will rise and we will try again.",
           "You are stronger than you think.",
           "It's okay to not be okay sometimes.",
           "This is a chapter, not your whole story."
       ],
       'activities': [
           "Watch a funny movie or comedy show",
           "Listen to uplifting music",
           "Go for a walk in nature",
           "Call someone who makes you laugh",
           "Do something creative like drawing or writing"
       ],
       'tasks': [
           "Write 3 things you accomplished today",
           "Look at photos that make you happy",
           "Do a random act of kindness",
           "Practice self-care: take a warm bath or shower",
           "Plan something to look forward to"
       ]
   },
   'Fear': {
       'quotes': [
           "Courage is not the absence of fear, but action in spite of it.",
           "You are braver than you believe, stronger than you seem.",
           "Fear is temporary, regret is forever.",
           "The only way out is through.",
           "You've survived 100% of your worst days so far."
       ],
       'activities': [
           "Practice grounding: 5-4-3-2-1 technique",
           "Do some gentle stretching or yoga",
           "Listen to guided meditation",
           "Take slow, deep breaths",
           "Hold a comforting object"
       ],
       'tasks': [
           "Break down your worry into smaller, manageable steps",
           "Write down your fears and challenge them",
           "Practice positive self-talk",
           "Focus on what you can control",
           "Remind yourself of past challenges you've overcome"
       ]
   },
   'Happy': {
       'quotes': [
           "Keep shining! Your happiness is contagious.",
           "You're doing great! Keep spreading those good vibes.",
           "Happiness looks good on you!",
           "Your smile can change the world.",
           "Life is beautiful, just like your smile!"
       ],
       'activities': [
           "Share your joy with someone you care about",
           "Take a photo to remember this moment",
           "Do something nice for someone else",
           "Dance to your favorite song",
           "Spend time in nature"
       ],
       'tasks': [
           "Write in a gratitude journal",
           "Plan a fun activity for later",
           "Compliment someone today",
           "Learn something new",
           "Set a positive goal for tomorrow"
       ]
   },
   'Neutral': {
       'quotes': [
           "A calm mind brings inner strength and self-confidence.",
           "Peace comes from within. Do not seek it without.",
           "Sometimes the most productive thing you can do is relax.",
           "In the midst of chaos, find your center.",
           "Stillness is the key to clarity."
       ],
       'activities': [
           "Try a new hobby or skill",
           "Read an interesting book",
           "Do some light exercise",
           "Organize your space",
           "Plan your day or week"
       ],
       'tasks': [
           "Set three small goals for today",
           "Practice mindfulness for 5 minutes",
           "Reach out to a friend you haven't spoken to",
           "Learn one new fact about something interesting",
           "Do something that challenges you slightly"
       ]
   },
   'Disgust': {
       'quotes': [
           "Focus on what brings you joy, not what disturbs you.",
           "You have the power to choose your thoughts.",
           "Redirect your energy toward positive things.",
           "This feeling will pass. You are in control.",
           "Find beauty in the world around you."
       ],
       'activities': [
           "Listen to your favorite uplifting music",
           "Look at beautiful art or nature photos",
           "Do something that makes you feel clean and fresh",
           "Practice positive visualization",
           "Engage in a hobby you enjoy"
       ],
       'tasks': [
           "Clean or organize your immediate space",
           "Focus on three beautiful things around you",
           "Practice positive affirmations",
           "Do something that makes you feel accomplished",
           "Shift your attention to something you love"
       ]
   },
   'Surprise': {
       'quotes': [
           "Life is full of surprises. Embrace them!",
           "Expect the unexpected and you'll never be disappointed.",
           "Surprise is the greatest gift which life can grant us.",
           "Stay curious and open to new experiences.",
           "The best adventures begin with a surprise."
       ],
       'activities': [
           "Try something completely new today",
           "Explore a new place or route",
           "Learn about a topic you've never studied",
           "Be spontaneous and do something unplanned",
           "Share your surprise with someone"
       ],
       'tasks': [
           "Write down what surprised you and why",
           "Plan a surprise for someone else",
           "Try a new recipe or food",
           "Take a different route to a familiar place",
           "Ask someone a question you've never asked before"
       ]
   }
}

class EmotionHelper:
   def __init__(self):
       self.last_emotion = None
       self.emotion_count = 0
       self.last_suggestion_time = 0
       self.current_suggestion = ""
       self.suggestion_type = ""
       
   def get_suggestion(self, emotion):
       current_time = time.time()
       
       # Only show new suggestion if emotion changed or 30 seconds passed
       if (emotion != self.last_emotion or 
           current_time - self.last_suggestion_time > 30):
           
           if emotion in emotion_responses:
               suggestion_types = ['quotes', 'activities', 'tasks']
               self.suggestion_type = random.choice(suggestion_types)
               suggestions = emotion_responses[emotion][self.suggestion_type]
               self.current_suggestion = random.choice(suggestions)
               self.last_suggestion_time = current_time
               
       self.last_emotion = emotion
       return self.current_suggestion, self.suggestion_type

def extract_features(image):
   """Enhanced feature extraction with normalization"""
   if image is None or image.size == 0:
       return None
   
   image = cv2.equalizeHist(image)
   image = cv2.resize(image, (48, 48))
   feature = np.array(image, dtype=np.float32)
   feature = feature.reshape(1, 48, 48, 1)
   return feature / 255.0

def detect_faces_improved(gray_frame, face_cascade_param=None, profile_cascade_param=None):
   """Improved face detection using multiple cascades and parameters"""
   # Use provided cascades if available, otherwise use global ones
   face_casc = face_cascade_param if face_cascade_param is not None else face_cascade
   profile_casc = profile_cascade_param if profile_cascade_param is not None else profile_cascade
   
   faces = face_casc.detectMultiScale(
       gray_frame, 
       scaleFactor=1.1,
       minNeighbors=5,
       minSize=(30, 30),
       maxSize=(300, 300),
       flags=cv2.CASCADE_SCALE_IMAGE
   )
   
   if len(faces) == 0:
       faces = face_casc.detectMultiScale(
           gray_frame,
           scaleFactor=1.05,
           minNeighbors=3,
           minSize=(20, 20),
           maxSize=(400, 400)
       )
   
   if len(faces) == 0:
       faces = profile_casc.detectMultiScale(
           gray_frame,
           scaleFactor=1.1,
           minNeighbors=5,
           minSize=(30, 30)
       )
   
   return faces

def draw_text_with_background(img, text, position, font_scale=0.6, color=(255, 255, 255), 
                           bg_color=(0, 0, 0), thickness=2):
   """Draw text with background rectangle"""
   x, y = position
   font = cv2.FONT_HERSHEY_SIMPLEX
   
   # Get text size
   (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
   
   # Draw background rectangle
   cv2.rectangle(img, (x, y - text_height - 5), (x + text_width, y + baseline), bg_color, -1)
   
   # Draw text
   cv2.putText(img, text, (x, y), font, font_scale, color, thickness)
   
   return text_height + 10

def wrap_text(text, max_width=50):
   """Wrap text to fit within specified width"""
   words = text.split()
   lines = []
   current_line = []
   
   for word in words:
       if len(' '.join(current_line + [word])) <= max_width:
           current_line.append(word)
       else:
           if current_line:
               lines.append(' '.join(current_line))
               current_line = [word]
           else:
               lines.append(word)
   
   if current_line:
       lines.append(' '.join(current_line))
   
   return lines

# Initialize
webcam = cv2.VideoCapture(0)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
webcam.set(cv2.CAP_PROP_FPS, 30)

labels = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Neutral', 5: 'Sad', 6: 'Surprise'}

emotion_colors = {
   'Angry': (0, 0, 255),
   'Disgust': (0, 128, 0),
   'Fear': (128, 0, 128),
   'Happy': (0, 255, 255),
   'Neutral': (255, 255, 255),
   'Sad': (255, 0, 0),
   'Surprise': (0, 165, 255)
}

helper = EmotionHelper()

print("Emotion Detection with Wellness Helper")
print("Press 'q' to quit, 's' to save screenshot, 'n' for new suggestion")

while True:
   ret, frame = webcam.read()
   if not ret:
       break
   
   frame = cv2.flip(frame, 1)
   gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
   gray = cv2.GaussianBlur(gray, (5, 5), 0)
   
   faces = detect_faces_improved(gray)
   
   try:
       for (x, y, w, h) in faces:
           padding = 10
           face_region = gray[max(0, y-padding):min(gray.shape[0], y+h+padding),
                             max(0, x-padding):min(gray.shape[1], x+w+padding)]
           
           if face_region.size > 0:
                features = extract_features(face_region)
                
                if features is not None and model is not None:
                    try:
                        prediction = model.predict(features, verbose=0)
                        confidence = np.max(prediction)
                        emotion_label = labels[np.argmax(prediction)]
                        
                        if confidence > 0.4:
                            # Draw face rectangle
                            color = emotion_colors.get(emotion_label, (255, 255, 255))
                            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                            
                            # Add emotion label
                            emotion_text = f"{emotion_label}: {confidence:.2f}"
                            text_y = y - 10 if y - 10 > 10 else y + h + 25
                            draw_text_with_background(frame, emotion_text, (x, text_y), 
                                                    color=(255, 255, 255), bg_color=color)
                            
                            # Get suggestion
                            suggestion, suggestion_type = helper.get_suggestion(emotion_label)
                            
                            if suggestion:
                                # Display suggestion in a panel
                                panel_height = 200
                                panel_width = 600
                                panel_x = 20
                                panel_y = frame.shape[0] - panel_height - 20
                                
                                # Draw suggestion panel
                                cv2.rectangle(frame, (panel_x, panel_y), 
                                            (panel_x + panel_width, panel_y + panel_height), 
                                            (0, 0, 0), -1)
                                cv2.rectangle(frame, (panel_x, panel_y), 
                                            (panel_x + panel_width, panel_y + panel_height), 
                                            color, 2)
                                
                                # Add suggestion title
                                title_map = {
                                    'quotes': 'Motivational Quote',
                                    'activities': 'Suggested Activity',
                                    'tasks': 'Helpful Task'
                                }
                                title = title_map.get(suggestion_type, 'Suggestion')
                                
                                current_y = panel_y + 25
                                current_y += draw_text_with_background(
                                    frame, title, (panel_x + 10, current_y), 
                                    font_scale=0.8, color=(0, 255, 255), bg_color=(0, 0, 0)
                                )
                                
                                # Add wrapped suggestion text
                                wrapped_lines = wrap_text(suggestion, 65)
                                for line in wrapped_lines:
                                    current_y += draw_text_with_background(
                                        frame, line, (panel_x + 10, current_y), 
                                        font_scale=0.5, color=(255, 255, 255), bg_color=(0, 0, 0)
                                    )
                                
                                # Add instruction
                                instruction = "Press 'n' for new suggestion"
                                draw_text_with_background(
                                    frame, instruction, (panel_x + 10, panel_y + panel_height - 15), 
                                    font_scale=0.4, color=(200, 200, 200), bg_color=(0, 0, 0)
                                )
                    except Exception as e:
                        print(f"Error during prediction: {e}")
                        continue
                else:
                    if model is None:
                        print("Error: Emotion detection model is not available")
                        cv2.putText(frame, "Model not available", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
       
       # Add controls info
       cv2.putText(frame, "Press 'q' to quit, 's' to save, 'n' for new suggestion", 
                  (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
       
       cv2.imshow("Emotion Detection & Wellness Helper", frame)
       
       key = cv2.waitKey(1) & 0xFF
       if key == ord('q'):
           break
       elif key == ord('s'):
           cv2.imwrite("emotion_detection_screenshot.jpg", frame)
           print("Screenshot saved!")
       elif key == ord('n'):
           # Force new suggestion
           helper.last_suggestion_time = 0
           
   except Exception as e:
       print(f"Error: {e}")
       continue

webcam.release()
cv2.destroyAllWindows()