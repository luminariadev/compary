import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
from skimage.metrics import mean_squared_error as mse

def calculate_quality_metrics(original_img_np, compressed_img_np):
    if original_img_np.shape != compressed_img_np.shape:
        return {"PSNR": "N/A", "SSIM": "N/A", "MSE": "N/A"}
        
    multichannel = len(original_img_np.shape) == 3 and original_img_np.shape[-1] == 3
    
    psnr_val = psnr(original_img_np, compressed_img_np, data_range=255)
    
    # scikit-image ssim requires channel_axis for multichannel
    if multichannel:
        ssim_val = ssim(original_img_np, compressed_img_np, channel_axis=-1, data_range=255)
    else:
        ssim_val = ssim(original_img_np, compressed_img_np, data_range=255)
        
    mse_val = mse(original_img_np, compressed_img_np)
    
    return {
        "PSNR": round(psnr_val, 2),
        "SSIM": round(ssim_val, 4),
        "MSE": round(mse_val, 2)
    }
