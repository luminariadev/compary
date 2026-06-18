import cv2
import numpy as np
from PIL import Image
import time

def compress_chroma_subsampling(input_path, output_path, subsampling_type="4:2:0"):
    start_time = time.time()
    
    img = Image.open(input_path)
    img_np = np.array(img.convert("RGB"))
    
    # Convert to YCrCb (OpenCV uses BGR by default for cvtColor, but we feed RGB)
    img_yuv = cv2.cvtColor(img_np, cv2.COLOR_RGB2YCrCb)
    y, cr, cb = cv2.split(img_yuv)
    
    h, w = y.shape
    
    if subsampling_type == "4:2:0":
        cr_sub = cv2.resize(cr, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        cb_sub = cv2.resize(cb, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
        cr_up = cv2.resize(cr_sub, (w, h), interpolation=cv2.INTER_LINEAR)
        cb_up = cv2.resize(cb_sub, (w, h), interpolation=cv2.INTER_LINEAR)
    elif subsampling_type == "4:2:2":
        cr_sub = cv2.resize(cr, (w // 2, h), interpolation=cv2.INTER_AREA)
        cb_sub = cv2.resize(cb, (w // 2, h), interpolation=cv2.INTER_AREA)
        cr_up = cv2.resize(cr_sub, (w, h), interpolation=cv2.INTER_LINEAR)
        cb_up = cv2.resize(cb_sub, (w, h), interpolation=cv2.INTER_LINEAR)
    else: # 4:4:4
        cr_up = cr
        cb_up = cb
        
    img_yuv_reconstructed = cv2.merge([y, cr_up, cb_up])
    img_rgb_reconstructed = cv2.cvtColor(img_yuv_reconstructed, cv2.COLOR_YCrCb2RGB)
    
    out_img = Image.fromarray(img_rgb_reconstructed)
    # Save with high HEVC quality to isolate the effect of our manual chroma subsampling
    out_img.save(output_path, "HEIF", quality=90)
    
    end_time = time.time()
    return end_time - start_time
