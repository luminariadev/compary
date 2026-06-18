import os

def calculate_compression_metrics(original_path, compressed_path, original_img_np):
    orig_size = os.path.getsize(original_path)
    comp_size = os.path.getsize(compressed_path)
    
    ratio = round(orig_size / comp_size, 2) if comp_size > 0 else 0
    space_savings = round((1 - (comp_size / orig_size)) * 100, 2) if orig_size > 0 else 0
    
    h, w = original_img_np.shape[:2]
    pixels = h * w
    bpp = round((comp_size * 8) / pixels, 4) if pixels > 0 else 0
    
    return {
        "Original Size (bytes)": orig_size,
        "Compressed Size (bytes)": comp_size,
        "Compression Ratio": ratio,
        "Space Savings (%)": space_savings,
        "BPP": bpp
    }
