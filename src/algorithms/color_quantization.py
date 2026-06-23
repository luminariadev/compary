import time
import warnings

import numpy as np
from PIL import Image
from sklearn.cluster import MiniBatchKMeans

warnings.filterwarnings("ignore", category=UserWarning)


def compress_color_quantization(
    input_path,
    output_path,
    n_colors=8,
    max_samples=8000,
    batch_size=8192,
    max_iter=25,
    quality=35
):
    start_time = time.time()

    img = Image.open(input_path).convert("RGB")
    img_np = np.array(img)

    h, w, _ = img_np.shape
    pixels = img_np.reshape(-1, 3)

    if len(pixels) > max_samples:
        rng = np.random.default_rng(42)
        sample_indices = rng.choice(
            pixels.shape[0],
            max_samples,
            replace=False
        )
        sample_pixels = pixels[sample_indices]
    else:
        sample_pixels = pixels

    kmeans = MiniBatchKMeans(
        n_clusters=n_colors,
        random_state=42,
        n_init=1,
        batch_size=batch_size,
        max_iter=max_iter,
        reassignment_ratio=0.01
    )

    kmeans.fit(sample_pixels)

    chunk_size = 500000
    labels_list = []

    for start in range(0, len(pixels), chunk_size):
        end = start + chunk_size
        labels = kmeans.predict(pixels[start:end])
        labels_list.append(labels)

    labels = np.concatenate(labels_list)

    centers = np.clip(kmeans.cluster_centers_, 0, 255).astype(np.uint8)
    quantized_pixels = centers[labels]
    quantized_img_np = quantized_pixels.reshape((h, w, 3))

    out_img = Image.fromarray(quantized_img_np, mode="RGB")
    out_img.save(output_path, "HEIF", quality=quality)

    end_time = time.time()
    return end_time - start_time