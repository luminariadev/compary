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

def process_and_display(img_path, original_np, algo_name, param):
    st.write(f"### {algo_name}")
    
    # Run Compression
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
            
    # Load Result
    comp_pil = Image.open(comp_path).convert("RGB")
    comp_np = np.array(comp_pil)
    
    # Calculate Metrics
    comp_metrics = calculate_compression_metrics(img_path, comp_path, original_np)
    qual_metrics = calculate_quality_metrics(original_np, comp_np)
    
    # Display Result
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
        
    return {
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

tab1, tab2, tab3, tab4 = st.tabs(["HEVC Quality", "Chroma Subsampling", "Color Quantization", "Komparasi Ketiganya"])

with tab1:
    st.header("HEVC Quality Reduction")
    hevc_file = st.file_uploader("Upload HEIC", type=["heic"], key="hevc_file")
    hevc_qual = st.slider("Quality", 1, 100, 10, key="hevc_qual")
    
    if hevc_file and st.button("Kompres - HEVC Quality"):
        # Save temp original
        temp_orig = os.path.join(tempfile.gettempdir(), f"orig_{int(time.time())}.heic")
        with open(temp_orig, "wb") as f:
            f.write(hevc_file.getbuffer())
            
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(orig_pil, caption="Original", use_container_width=True)
            orig_size = os.path.getsize(temp_orig)
            st.metric("Original Size", f"{orig_size / 1024:.2f} KB")
            
        with col2:
            process_and_display(temp_orig, orig_np, "HEVC Quality", hevc_qual)

with tab2:
    st.header("Chroma Subsampling")
    chroma_file = st.file_uploader("Upload HEIC", type=["heic"], key="chroma_file")
    chroma_val = st.selectbox("Subsampling Format", ["4:2:0", "4:2:2", "4:4:4"], key="chroma_val")
    
    if chroma_file and st.button("Kompres - Chroma Subsampling"):
        temp_orig = os.path.join(tempfile.gettempdir(), f"orig_{int(time.time())}.heic")
        with open(temp_orig, "wb") as f:
            f.write(chroma_file.getbuffer())
            
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(orig_pil, caption="Original", use_container_width=True)
            orig_size = os.path.getsize(temp_orig)
            st.metric("Original Size", f"{orig_size / 1024:.2f} KB")
            
        with col2:
            process_and_display(temp_orig, orig_np, "Chroma Subsampling", chroma_val)

with tab3:
    st.header("Color Quantization")
    color_file = st.file_uploader("Upload HEIC", type=["heic"], key="color_file")
    color_val = st.number_input("Number of Colors (K-Means)", min_value=2, max_value=256, value=4, key="color_val")
    
    if color_file and st.button("Kompres - Color Quantization"):
        temp_orig = os.path.join(tempfile.gettempdir(), f"orig_{int(time.time())}.heic")
        with open(temp_orig, "wb") as f:
            f.write(color_file.getbuffer())
            
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(orig_pil, caption="Original", use_container_width=True)
            orig_size = os.path.getsize(temp_orig)
            st.metric("Original Size", f"{orig_size / 1024:.2f} KB")
            
        with col2:
            process_and_display(temp_orig, orig_np, "Color Quantization", int(color_val))

with tab4:
    st.header("Komparasi Ketiga Algoritma")
    st.write("Silakan upload 1 gambar dan sesuaikan parameter, kemudian aplikasi akan memproses ketiga algoritma sekaligus untuk disandingkan.")
    
    comp_file = st.file_uploader("Upload HEIC Image", type=["heic"], key="comp_file")
    
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        c_hevc_qual = st.slider("HEVC Quality", 1, 100, 10, key="c_hevc_qual")
    with c_col2:
        c_chroma_val = st.selectbox("Chroma Subsampling Format", ["4:2:0", "4:2:2", "4:4:4"], key="c_chroma_val")
    with c_col3:
        c_color_val = st.number_input("Num Colors", min_value=2, max_value=256, value=4, key="c_color_val")
        
    if comp_file and st.button("Jalankan Komparasi", type="primary"):
        temp_orig = os.path.join(tempfile.gettempdir(), f"orig_{int(time.time())}.heic")
        with open(temp_orig, "wb") as f:
            f.write(comp_file.getbuffer())
            
        orig_pil = Image.open(temp_orig).convert("RGB")
        orig_np = np.array(orig_pil)
        
        st.subheader("Gambar Original")
        st.image(orig_pil, caption="Original", width=400)
        
        st.divider()
        st.subheader("Hasil Kompresi Bersebelahan")
        res_col1, res_col2, res_col3 = st.columns(3)
        
        results = []
        with res_col1:
            res1 = process_and_display(temp_orig, orig_np, "HEVC Quality", c_hevc_qual)
            results.append(res1)
        with res_col2:
            res2 = process_and_display(temp_orig, orig_np, "Chroma Subsampling", c_chroma_val)
            results.append(res2)
        with res_col3:
            res3 = process_and_display(temp_orig, orig_np, "Color Quantization", int(c_color_val))
            results.append(res3)
            
        st.divider()
        st.subheader("Tabel Rekapitulasi Metrik")
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
