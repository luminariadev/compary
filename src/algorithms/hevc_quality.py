from PIL import Image
import time

def compress_hevc_quality(input_path, output_path, quality=50):
    start_time = time.time()
    
    img = Image.open(input_path)
    img.save(output_path, "HEIF", quality=quality)
    
    end_time = time.time()
    return end_time - start_time
