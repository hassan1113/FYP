from PIL import Image
import numpy as np

image_path = r"C:\Users\Syscom\OneDrive - FAST National University\Desktop\Emotion_Detection\images\test\angry\854.jpg"
try:
    img = Image.open(image_path)
    print(f"Image format: {img.format}")
    print(f"Image size: {img.size}")
    print(f"Image mode: {img.mode}")
    print(f"Image info: {img.info}")
    
    # Convert to numpy array to check content
    img_array = np.array(img)
    print(f"Array shape: {img_array.shape}")
    print(f"Array dtype: {img_array.dtype}")
    print(f"Unique values: {np.unique(img_array)}")
    
except Exception as e:
    print(f"Error analyzing image: {e}")
