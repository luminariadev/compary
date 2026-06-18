# Sistem Komparasi Kompresi Citra HEIC
## Tugas Sistem Multimedia - Kelompok 9

### Deskripsi Proyek
Aplikasi Python untuk membandingkan 3 algoritma kompresi pada gambar format HEIC:
1. HEVC Quality Reduction - Mengurangi kualitas kompresi HEVC (H.265)
2. Chroma Subsampling - Mengurangi resolusi warna (YUV 4:2:0, 4:2:2, 4:1:1)
3. Color Quantization - Mengurangi jumlah warna menggunakan K-Means clustering

### Teknologi
- Python 3.10+
- pillow-heif - Membaca dan menulis file HEIC
- OpenCV (cv2) - Manipulasi gambar
- scikit-image - Metrik kualitas (PSNR, SSIM)
- scikit-learn - K-Means clustering
- tkinter - GUI (built-in Python)
- matplotlib - Visualisasi grafik
- numpy - Komputasi numerik

### Struktur Folder
```
kelompok9-heic-compression/
├── src/
│   ├── algorithms/
│   │   ├── hevc_quality.py
│   │   ├── chroma_subsampling.py
│   │   └── color_quantization.py
│   ├── metrics/
│   │   ├── quality_metrics.py
│   │   └── compression_metrics.py
│   ├── gui/
│   │   └── main_window.py
│   └── main.py
├── tests/
├── samples/
├── results/
├── requirements.txt
├── run.py
└── README.md
```

### Instalasi
```bash
git clone https://github.com/username/kelompok9-heic-compression.git
cd kelompok9-heic-compression
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

### Metrik Evaluasi
| Metrik | Deskripsi |
|--------|-----------|
| Original Size | Ukuran file asli (bytes) |
| Compressed Size | Ukuran file setelah kompresi (bytes) |
| Compression Ratio | Rasio ukuran asli/kompresi |
| PSNR | Peak Signal-to-Noise Ratio (dB) - Semakin tinggi semakin baik |
| SSIM | Structural Similarity Index (0-1) - Semakin tinggi semakin baik |
| MSE | Mean Squared Error - Semakin rendah semakin baik |
| Processing Time | Waktu kompresi (detik) |
| BPP | Bits Per Pixel |
| Space Savings | Persentase penghematan ruang |

### Fitur Aplikasi
1. Load HEIC Image - Buka file gambar HEIC
2. Parameter Control - Atur parameter tiap algoritma
3. One-Click Compression - Jalankan semua algoritma sekaligus
4. Preview - Tampilkan original vs compressed
5. Metrics Table - Tabel perbandingan metrik
6. Export Results - Simpan hasil ke CSV atau JSON

### Timeline Pengerjaan (2 Minggu)
**Minggu 1:**
- Hari 1-2: Setup environment, install dependencies
- Hari 3-4: Implementasi HEVC Quality Reduction
- Hari 5-6: Implementasi Chroma Subsampling
- Hari 7: Implementasi Color Quantization

**Minggu 2:**
- Hari 1-2: Implementasi metrik kualitas
- Hari 3-4: Buat GUI dengan tkinter
- Hari 5-6: Testing, debugging, optimasi
- Hari 7: Finalisasi

### Referensi
- HEVC / H.265 Compression - https://en.wikipedia.org/wiki/H.265
- Chroma Subsampling - https://en.wikipedia.org/wiki/Chroma_subsampling
- Color Quantization - https://en.wikipedia.org/wiki/Color_quantization
- Pillow-HEIF - https://github.com/bigcat88/pillow_heif
- OpenCV - https://docs.opencv.org/
- scikit-image - https://scikit-image.org/
- scikit-learn - https://scikit-learn.org/
