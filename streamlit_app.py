import streamlit as st
import os
import tempfile
import time
from PIL import Image
import numpy as np
from pillow_heif import register_heif_opener
import pandas as pd

from src.algorithms.hevc_quality import compress_hevc_quality
from src.algorithms.chroma_subsampling import compress_chroma_subsampling
from src.algorithms.color_quantization import compress_color_quantization
from src.metrics.quality_metrics import calculate_quality_metrics
from src.metrics.compression_metrics import calculate_compression_metrics

# Register HEIF Opener
register_heif_opener()

st.set_page_config(page_title="HEIC Compression Compary", layout="wide", page_icon="🖼️")

st.title("HEIC Compression Comparison")
st.markdown("Aplikasi komparasi 3 Algoritma Kompresi untuk format HEIC (Kelompok 9). Mode Dark/Light dapat diubah dari menu Settings pojok kanan atas.")

if "history" not in st.session_state:
    st.session_state["history"] = []

def handle_upload(uploaded_file):
    """Save uploaded file to temp. If not HEIC, convert to HEIC first."""
    temp_dir = tempfile.gettempdir()
    base_name = uploaded_file.name.lower()
    
    if base_name.endswith(".heic"):
        temp_orig = os.path.join(temp_dir, f"orig_{int(time.time()*1000)}.heic")
        with open(temp_orig, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return temp_orig
    else:
        # Convert to HEIC
        temp_orig = os.path.join(temp_dir, f"orig_{int(time.time()*1000)}.heic")
        img = Image.open(uploaded_file).convert("RGB")
        img.save(temp_orig, "HEIF", quality=100)
        st.info(f"File {uploaded_file.name} otomatis dikonversi ke HEIC untuk diproses.")
        return temp_orig

def process_and_display(img_path, original_np, algo_name, param):
    st.write(f"### {algo_name}")
    
    temp_dir = tempfile.gettempdir()
    comp_path = os.path.join(temp_dir, f"comp_{int(time.time()*1000)}.heic")
    
    time_taken = 0
    with st.spinner(f"Memproses {algo_name}..."):
        if algo_name == "HEVC Quality":
            time_taken = compress_hevc_quality(img_path, comp_path, param)
        elif algo_name == "Chroma Subsampling":
            time_taken = compress_chroma_subsampling(img_path, comp_path, param)
        elif algo_name == "Color Quantization":
            time_taken = compress_color_quantization(img_path, comp_path, param)
            
    comp_pil = Image.open(comp_path).convert("RGB")
    comp_np = np.array(comp_pil)
    
    comp_metrics = calculate_compression_metrics(img_path, comp_path, original_np)
    qual_metrics = calculate_quality_metrics(original_np, comp_np)
    
    st.image(comp_pil, caption=f"Hasil: {algo_name}", use_container_width=True)
    
    st.markdown("**Metrik Performa:**")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.metric("Time", f"{time_taken:.2f} s")
        st.metric("Space Savings", f"{comp_metrics['Space Savings (%)']}%")
        st.metric("Size", f"{comp_metrics['Compressed Size (bytes)'] / 1024:.2f} KB")
    with m_col2:
        st.metric("PSNR", f"{qual_metrics['PSNR']} dB")
        st.metric("SSIM", f"{qual_metrics['SSIM']}")
        st.metric("MSE", f"{qual_metrics['MSE']}")
        
    result_dict = {
        "Algorithm": algo_name,
        "Parameter": param,
        "Time (s)": round(time_taken, 2),
        "Orig Size (B)": comp_metrics["Original Size (bytes)"],
        "Comp Size (B)": comp_metrics["Compressed Size (bytes)"],
        "Space Save (%)": comp_metrics["Space Savings (%)"],
        "BPP": comp_metrics["BPP"],
        "PSNR": qual_metrics["PSNR"],
        "SSIM": qual_metrics["SSIM"],
        "MSE": qual_metrics["MSE"]
    }
    st.session_state["history"].append(result_dict)
    return result_dict

tabs = st.tabs(["HEVC Quality", "Chroma Subsampling", "Color Quantization", "Komparasi", "Analisis Grafik Data", "Metrik Teoritis", "Metrik Empiris"])

# Tab 1: HEVC
with tabs[0]:
    st.header("HEVC Quality Reduction")
    hevc_file = st.file_uploader("Upload Image (HEIC/JPG/PNG)", type=["heic", "jpg", "jpeg", "png"], key="hevc_file")
    hevc_qual = st.slider("Quality", 1, 100, 10, key="hevc_qual")
    
    if hevc_file and st.button("Kompres - HEVC Quality"):
        temp_orig = handle_upload(hevc_file)
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(orig_pil, caption="Original", use_container_width=True)
            st.metric("Original Size", f"{os.path.getsize(temp_orig) / 1024:.2f} KB")
        with col2:
            process_and_display(temp_orig, orig_np, "HEVC Quality", hevc_qual)

# Tab 2: Chroma
with tabs[1]:
    st.header("Chroma Subsampling")
    chroma_file = st.file_uploader("Upload Image (HEIC/JPG/PNG)", type=["heic", "jpg", "jpeg", "png"], key="chroma_file")
    chroma_val = st.selectbox("Subsampling Format", ["4:2:0", "4:2:2", "4:4:4"], key="chroma_val")
    
    if chroma_file and st.button("Kompres - Chroma Subsampling"):
        temp_orig = handle_upload(chroma_file)
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(orig_pil, caption="Original", use_container_width=True)
            st.metric("Original Size", f"{os.path.getsize(temp_orig) / 1024:.2f} KB")
        with col2:
            process_and_display(temp_orig, orig_np, "Chroma Subsampling", chroma_val)

# Tab 3: Color Quantization
with tabs[2]:
    st.header("Color Quantization")
    color_file = st.file_uploader("Upload Image (HEIC/JPG/PNG)", type=["heic", "jpg", "jpeg", "png"], key="color_file")
    color_val = st.number_input("Number of Colors (K-Means)", min_value=2, max_value=256, value=4, key="color_val")
    
    if color_file and st.button("Kompres - Color Quantization"):
        temp_orig = handle_upload(color_file)
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(orig_pil, caption="Original", use_container_width=True)
            st.metric("Original Size", f"{os.path.getsize(temp_orig) / 1024:.2f} KB")
        with col2:
            process_and_display(temp_orig, orig_np, "Color Quantization", int(color_val))

# Tab 4: Komparasi
with tabs[3]:
    st.header("Komparasi Ketiga Algoritma")
    st.write("Silakan upload 1 gambar dan sesuaikan parameter. Gambar non-HEIC akan otomatis dikonversi ke HEIC untuk menjadi baseline komparasi.")
    
    comp_file = st.file_uploader("Upload Image (HEIC/JPG/PNG)", type=["heic", "jpg", "jpeg", "png"], key="comp_file")
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        c_hevc_qual = st.slider("HEVC Quality", 1, 100, 10, key="c_hevc_qual")
    with c_col2:
        c_chroma_val = st.selectbox("Chroma Subsampling Format", ["4:2:0", "4:2:2", "4:4:4"], key="c_chroma_val")
    with c_col3:
        c_color_val = st.number_input("Num Colors", min_value=2, max_value=256, value=4, key="c_color_val")
        
    if comp_file and st.button("Jalankan Komparasi", type="primary"):
        temp_orig = handle_upload(comp_file)
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        st.subheader("Gambar Original (Baseline)")
        st.image(orig_pil, caption="Original", width=400)
        
        st.divider()
        st.subheader("Hasil Kompresi Bersebelahan")
        res_col1, res_col2, res_col3 = st.columns(3)
        
        with res_col1:
            process_and_display(temp_orig, orig_np, "HEVC Quality", c_hevc_qual)
        with res_col2:
            process_and_display(temp_orig, orig_np, "Chroma Subsampling", c_chroma_val)
        with res_col3:
            process_and_display(temp_orig, orig_np, "Color Quantization", int(c_color_val))

# Tab 5: Grafik Data
with tabs[4]:
    st.header("Analisis Grafik Data")
    if not st.session_state["history"]:
        st.info("Belum ada data kompresi. Silakan jalankan kompresi di tab sebelumnya terlebih dahulu.")
    else:
        df = pd.DataFrame(st.session_state["history"])
        
        # Agregasi data terbaru untuk setiap algoritma
        df_last = df.drop_duplicates(subset=["Algorithm"], keep="last")
        
        st.subheader("Waktu Proses (detik)")
        st.bar_chart(df_last.set_index("Algorithm")["Time (s)"])
        
        st.subheader("Penghematan Ruang / Space Savings (%)")
        st.bar_chart(df_last.set_index("Algorithm")["Space Save (%)"])
        
        st.subheader("Kualitas Gambar (PSNR)")
        st.bar_chart(df_last.set_index("Algorithm")["PSNR"])
        
        st.subheader("Kualitas Gambar (SSIM)")
        st.line_chart(df_last.set_index("Algorithm")["SSIM"])

# Tab 6: Metrik Teoritis
with tabs[5]:
    st.header("Tabel Metrik Komparasi Teoritis")
    
    st.markdown("""
    Berdasarkan tinjauan teori sistem multimedia, berikut adalah komparasi karakteristik dari ketiga algoritma kompresi tersebut:
    """)
    
    teori_data = {
        "Aspek Komparasi": ["Fokus Utama Kompresi", "Kompleksitas Komputasi", "Rata-rata Space Savings", "Dampak Visual Utama", "Sifat Kompresi"],
        "HEVC Quality Reduction": ["Pengurangan detail/resolusi frekuensi tinggi", "Tinggi (Encoding video/gambar full)", "Sangat Tinggi (Bisa >80%)", "Blurring, blockiness pada kualitas rendah", "Lossy"],
        "Chroma Subsampling": ["Pengurangan resolusi warna (CbCr) dengan mempertahankan Luminance (Y)", "Rendah (Hanya konversi & resize channel warna)", "Rendah - Sedang (Maks ~50% di 4:2:0)", "Kehilangan detail warna pada tepian tajam", "Lossy (hanya warna)"],
        "Color Quantization": ["Pengurangan jumlah warna unik (palette)", "Sedang - Tinggi (Algoritma Clustering/K-Means)", "Sedang (Sangat bergantung jumlah N warna)", "Color banding (warna nge-blok), posterisasi", "Lossy (palette restriction)"]
    }
    
    st.dataframe(pd.DataFrame(teori_data).set_index("Aspek Komparasi"), use_container_width=True)

# Tab 7: Metrik Empiris
with tabs[6]:
    st.header("Metrik Hasil Empiris (Real-time)")
    st.write("Tabel ini menyimpan seluruh riwayat kompresi yang Anda lakukan selama sesi ini berjalan.")
    
    if not st.session_state["history"]:
        st.info("Belum ada data empiris.")
    else:
        df_history = pd.DataFrame(st.session_state["history"])
        st.dataframe(df_history, use_container_width=True)
        
        csv = df_history.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Log CSV",
            data=csv,
            file_name=f'komparasi_empiris_{int(time.time())}.csv',
            mime='text/csv',
        )
