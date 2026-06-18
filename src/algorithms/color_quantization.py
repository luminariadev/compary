import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
import time
import warnings

# Suppress sklearn warnings about memory leak on Windows
warnings.filterwarnings('ignore', category=UserWarning)

def compress_color_quantization(input_path, output_path, n_colors=16):
    start_time = time.time()
    
    img = Image.open(input_path)
    img_np = np.array(img.convert("RGB"))
    h, w, c = img_np.shape
    
    # Reshape to a 2D array of pixels
    pixels = img_np.reshape(-1, 3)
    
    # Subsample pixels for KMeans to speed up the process if the image is too large
    if len(pixels) > 100000:
        sample_pixels = pixels[np.random.choice(pixels.shape[0], 100000, replace=False)]
    else:
        sample_pixels = pixels

    # Apply KMeans
    kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    kmeans.fit(sample_pixels)
    
    labels = kmeans.predict(pixels)
    centers = kmeans.cluster_centers_.astype(np.uint8)
    
    # Reconstruct the image
    quantized_pixels = centers[labels]
    quantized_img_np = quantized_pixels.reshape((h, w, 3))
    
    out_img = Image.fromarray(quantized_img_np)
    # Save with high quality to isolate color quantization effect
    out_img.save(output_path, "HEIF", quality=90)
    
    end_time = time.time()
    return end_time - start_time
