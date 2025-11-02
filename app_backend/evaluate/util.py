import numpy as np
import tensorflow as tf
import os
from PIL import Image

def convert_to_serializable(obj):
    """ Recursively converts numpy and tf types to native Python types for JSON serialization """
    if isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, tf.Tensor):
        return convert_to_serializable(obj.numpy())
    elif isinstance(obj, dict):
        return {k: convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_serializable(v) for v in obj]
    else:
        return obj

def load_images_from_directory(directory_path, target_size=(299, 299)):
    """ Recursively loads all images from subdirectories for Overall FID/IS """
    images = []
    if not os.path.exists(directory_path):
        return np.array(images)
        
    for subdir in os.listdir(directory_path):
        subdir_path = os.path.join(directory_path, subdir)
        if os.path.isdir(subdir_path):
            for filename in os.listdir(subdir_path):
                img_path = os.path.join(subdir_path, filename)
                try:
                    img = Image.open(img_path).convert('RGB')
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                    img = np.array(img)
                    if img.shape == (299, 299, 3):
                        images.append(img)
                except Exception:
                    pass # Ignore failed image loads
    return np.array(images)

def load_images_from_class_directory(directory_path, target_size=(299, 299)):
    """ Loads images from a single directory (non-recursive) for Per-Class FID """
    images = []
    if not os.path.exists(directory_path):
        return np.array([])
        
    for filename in os.listdir(directory_path):
        img_path = os.path.join(directory_path, filename)
        try:
            img = Image.open(img_path).convert('RGB')
            img = img.resize(target_size, Image.Resampling.LANCZOS)
            img = np.array(img)
            if img.shape == (299, 299, 3):
                images.append(img)
        except Exception:
            pass # Ignore failed image loads
    
    return np.array(images)

def preprocess_images(images):
    """ Preprocesses images for InceptionV3 """
    images_tf = tf.convert_to_tensor(images, dtype=tf.float32)
    images_tf = tf.image.resize(images_tf, (299, 299))
    images_tf = tf.keras.applications.inception_v3.preprocess_input(images_tf)
    return images_tf