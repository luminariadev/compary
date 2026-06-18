import os
import numpy as np
from PIL import Image, ImageDraw
from pillow_heif import register_heif_opener

register_heif_opener()

os.makedirs("samples", exist_ok=True)

# Sample 1: Gradient
h, w = 800, 800
gradient = np.zeros((h, w, 3), dtype=np.uint8)
for y in range(h):
    for x in range(w):
        gradient[y, x] = [int((x/w)*255), int((y/h)*255), int(((x+y)/(w+h))*255)]
        
img1 = Image.fromarray(gradient)
img1.save("samples/sample1_gradient.heic", "HEIF", quality=90)

# Sample 2: Shapes
img2 = Image.new("RGB", (800, 800), "white")
draw = ImageDraw.Draw(img2)
draw.rectangle([100, 100, 400, 400], fill="red", outline="black")
draw.ellipse([400, 400, 700, 700], fill="blue", outline="black")
draw.polygon([(100, 700), (300, 500), (400, 700)], fill="green", outline="black")

img2.save("samples/sample2_shapes.heic", "HEIF", quality=90)

print("Berhasil membuat file HEIC sample1_gradient.heic dan sample2_shapes.heic di folder samples/")
