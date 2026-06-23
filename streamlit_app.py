import os
import tempfile
import time
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from pillow_heif import register_heif_opener

from src.algorithms.chroma_subsampling import compress_chroma_subsampling
from src.algorithms.color_quantization import compress_color_quantization
from src.algorithms.hevc_quality import compress_hevc_quality
from src.metrics.compression_metrics import calculate_compression_metrics
from src.metrics.quality_metrics import calculate_quality_metrics


register_heif_opener()

st.set_page_config(
    page_title="HEIC Compression Lab",
    page_icon=":camera:",
    layout="wide",
    initial_sidebar_state="expanded",
)


APP_CSS = """
<style>
    .main .block-container {
        max-width: 1320px;
        padding-top: 1.35rem;
        padding-bottom: 2rem;
    }
    .hero {
        border: 1px solid #d7dde8;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        background:
            linear-gradient(135deg, rgba(20, 184, 166, 0.13), rgba(59, 130, 246, 0.10)),
            rgba(255, 255, 255, 0.82);
    }
    .hero h1 {
        margin: 0 0 0.35rem 0;
        font-size: 1.9rem;
        line-height: 1.15;
        letter-spacing: 0;
    }
    .hero p {
        margin: 0;
        color: #4b5563;
        font-size: 0.98rem;
    }
    [data-testid="stMetric"] {
        border: 1px solid #d7dde8;
        border-radius: 8px;
        padding: 0.72rem 0.85rem;
        background: rgba(255, 255, 255, 0.78);
    }
    div[data-testid="stImage"] img {
        border: 1px solid #d7dde8;
        border-radius: 8px;
    }
    .status-ok {
        border-left: 5px solid #16a34a;
        border-radius: 8px;
        padding: 0.78rem 0.95rem;
        background: #ecfdf5;
        color: #14532d;
        margin: 0.35rem 0 0.75rem;
    }
    .status-warn {
        border-left: 5px solid #dc2626;
        border-radius: 8px;
        padding: 0.78rem 0.95rem;
        background: #fef2f2;
        color: #7f1d1d;
        margin: 0.35rem 0 0.75rem;
    }
    .muted {
        color: #536175;
        margin-top: -0.2rem;
        margin-bottom: 0.8rem;
    }
    @media (prefers-color-scheme: dark) {
        .hero, [data-testid="stMetric"] {
            background: rgba(17, 24, 39, 0.78);
            border-color: #334155;
        }
        .hero p, .muted {
            color: #cbd5e1;
        }
    }
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)


ALGORITHM_OPTIONS = {
    "HEVC Quality": {
        "runner": compress_hevc_quality,
        "suffix": "hevc",
        "description": "Menurunkan kualitas encoder HEIC/HEVC.",
    },
    "Chroma Subsampling": {
        "runner": compress_chroma_subsampling,
        "suffix": "chroma",
        "description": "Mengurangi resolusi warna dengan luminance tetap dijaga.",
    },
    "Color Quantization": {
        "runner": compress_color_quantization,
        "suffix": "color",
        "description": "Mengurangi jumlah warna unik dengan clustering.",
    },
}


if "history" not in st.session_state:
    st.session_state["history"] = []
if "compare_results" not in st.session_state:
    st.session_state["compare_results"] = []
if "compare_visuals" not in st.session_state:
    st.session_state["compare_visuals"] = []
if "single_results" not in st.session_state:
    st.session_state["single_results"] = []
if "single_visuals" not in st.session_state:
    st.session_state["single_visuals"] = []


def format_bytes(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def make_run_dir():
    return tempfile.mkdtemp(prefix="heic_batch_")


def safe_stem(filename):
    stem = Path(filename).stem
    cleaned = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in stem)
    return cleaned[:60] or "image"


def save_uploaded_heic(uploaded_file, run_dir, index):
    import io
    file_ext = Path(uploaded_file.name).suffix.lower()
    output_path = os.path.join(run_dir, f"{index:02d}_{safe_stem(uploaded_file.name)}.heic")
    
    file_bytes = uploaded_file.getvalue()
    
    if file_ext in [".heic", ".heif"]:
        with open(output_path, "wb") as output:
            output.write(file_bytes)
        try:
            # Uji apakah file HEIC ini valid/bisa dibaca
            with Image.open(output_path) as img:
                img.verify()
        except Exception:
            # Jika gagal, mungkin ini JPG yang di-rename atau corrupt. Kita coba convert ulang.
            try:
                img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
                img.save(output_path, "HEIF", quality=100)
            except Exception as e:
                raise ValueError(f"File corrupt atau format tidak didukung.")
    else:
        # Otomatis konversi file JPG/PNG ke HEIC
        try:
            img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
            img.save(output_path, "HEIF", quality=100)
        except Exception as e:
            raise ValueError(f"Gagal mengonversi file: {e}")
            
    return output_path


def get_param_for_algorithm(algo_name, hevc_quality, chroma_value, color_count):
    if algo_name == "HEVC Quality":
        return int(hevc_quality)
    if algo_name == "Chroma Subsampling":
        return chroma_value
    return int(color_count)


def compress_one(original_path, original_np, original_name, index, algo_name, param, run_dir):
    suffix = ALGORITHM_OPTIONS[algo_name]["suffix"]
    output_path = os.path.join(
        run_dir,
        f"{index:02d}_{safe_stem(original_name)}_{suffix}_{int(time.time() * 1000)}.heic",
    )

    runner = ALGORITHM_OPTIONS[algo_name]["runner"]
    time_taken = runner(original_path, output_path, param)

    compressed_pil = Image.open(output_path).convert("RGB")
    compressed_np = np.array(compressed_pil)
    compression_metrics = calculate_compression_metrics(original_path, output_path, original_np)
    quality_metrics = calculate_quality_metrics(original_np, compressed_np)

    result = {
        "File": original_name,
        "Algorithm": algo_name,
        "Parameter": param,
        "Time (s)": round(time_taken, 3),
        "Original Size": format_bytes(compression_metrics["Original Size (bytes)"]),
        "Compressed Size": format_bytes(compression_metrics["Compressed Size (bytes)"]),
        "Original Size (bytes)": compression_metrics["Original Size (bytes)"],
        "Compressed Size (bytes)": compression_metrics["Compressed Size (bytes)"],
        "Compression Ratio": compression_metrics["Compression Ratio"],
        "Space Save (%)": compression_metrics["Space Savings (%)"],
        "BPP": compression_metrics["BPP"],
        "PSNR": quality_metrics["PSNR"],
        "SSIM": quality_metrics["SSIM"],
        "MSE": quality_metrics["MSE"],
    }

    visual = {
        "File": original_name,
        "Algorithm": algo_name,
        "Parameter": param,
        "Original Path": original_path,
        "Compressed Path": output_path,
        "Original Size": result["Original Size"],
        "Compressed Size": result["Compressed Size"],
        "Space Save (%)": result["Space Save (%)"],
        "PSNR": result["PSNR"],
        "SSIM": result["SSIM"],
    }
    return result, visual


def run_batch(uploaded_files, algorithms, hevc_quality, chroma_value, color_count, mode_label):
    run_dir = make_run_dir()
    batch_results = []
    batch_visuals = []
    total_steps = len(uploaded_files) * len(algorithms)
    current_step = 0
    progress = st.progress(0, text="Menyiapkan file HEIC...")

    for file_index, uploaded_file in enumerate(uploaded_files, start=1):
        try:
            original_path = save_uploaded_heic(uploaded_file, run_dir, file_index)
            original_pil = Image.open(original_path).convert("RGB")
            original_np = np.array(original_pil)
        except Exception as e:
            st.warning(f"File '{uploaded_file.name}' dilewati karena bermasalah: {e}")
            current_step += len(algorithms)
            continue

        for algo_name in algorithms:
            param = get_param_for_algorithm(algo_name, hevc_quality, chroma_value, color_count)
            progress.progress(
                current_step / total_steps,
                text=f"{mode_label}: memproses {uploaded_file.name} dengan {algo_name}...",
            )
            result, visual = compress_one(
                original_path,
                original_np,
                uploaded_file.name,
                file_index,
                algo_name,
                param,
                run_dir,
            )
            batch_results.append(result)
            batch_visuals.append(visual)
            current_step += 1

    progress.progress(1.0, text="Selesai memproses minimal 10 file.")
    return batch_results, batch_visuals


def table_columns():
    return [
        "File",
        "Algorithm",
        "Parameter",
        "Time (s)",
        "Original Size",
        "Compressed Size",
        "Compression Ratio",
        "Space Save (%)",
        "BPP",
        "PSNR",
        "SSIM",
        "MSE",
    ]


def render_summary_metrics(df_results):
    avg_space = pd.to_numeric(df_results["Space Save (%)"], errors="coerce").mean()
    avg_psnr = pd.to_numeric(df_results["PSNR"], errors="coerce").mean()
    avg_ssim = pd.to_numeric(df_results["SSIM"], errors="coerce").mean()
    avg_time = pd.to_numeric(df_results["Time (s)"], errors="coerce").mean()

    cols = st.columns(4)
    cols[0].metric("File Diuji", df_results["File"].nunique())
    cols[1].metric("Rata-rata Saving", f"{avg_space:.2f}%")
    cols[2].metric("Rata-rata PSNR", f"{avg_psnr:.2f} dB")
    cols[3].metric("Rata-rata Waktu", f"{avg_time:.2f} s")
    st.caption(f"Rata-rata SSIM: {avg_ssim:.4f}")


def render_visual_outputs(visuals, compare_mode):
    st.subheader("Output Gambar")
    st.markdown(
        "<p class='muted'>Hasil gambar muncul lebih dulu. Pilih file untuk melihat before/after hasil kompresi.</p>",
        unsafe_allow_html=True,
    )

    files = sorted({item["File"] for item in visuals})
    selected_file = st.selectbox("Pilih file hasil pengujian", files, key=f"visual_file_{compare_mode}")
    selected_visuals = [item for item in visuals if item["File"] == selected_file]
    before_path = selected_visuals[0]["Original Path"]

    if len(selected_visuals) == 3:
        before_col, hevc_col, chroma_col, color_col = st.columns(4)
        before_col.image(Image.open(before_path).convert("RGB"), caption="Before", use_container_width=True)
        for col, item in zip([hevc_col, chroma_col, color_col], selected_visuals):
            col.image(
                Image.open(item["Compressed Path"]).convert("RGB"),
                caption=f"{item['Algorithm']} ({item['Parameter']})",
                use_container_width=True,
            )
            col.metric("Saving", f"{item['Space Save (%)']}%")
    else:
        item = selected_visuals[0]
        before_col, after_col = st.columns(2)
        before_col.image(Image.open(before_path).convert("RGB"), caption="Before", use_container_width=True)
        before_col.metric("Original Size", item["Original Size"])
        after_col.image(
            Image.open(item["Compressed Path"]).convert("RGB"),
            caption=f"After: {item['Algorithm']} ({item['Parameter']})",
            use_container_width=True,
        )
        after_col.metric("Compressed Size", item["Compressed Size"])


def render_table_outputs(df_results, mode_label):
    st.subheader("Tabel Hasil Pengujian")
    display_df = df_results[table_columns()]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    csv = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Tabel CSV",
        data=csv,
        file_name=f"hasil_{mode_label}_{int(time.time())}.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_chart_outputs(df_results):
    st.subheader("Grafik Perbandingan")
    numeric_cols = ["Time (s)", "Space Save (%)", "PSNR", "SSIM", "MSE", "BPP"]
    chart_df = df_results.copy()
    for col in numeric_cols:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    avg_df = (
        chart_df.groupby("Algorithm", as_index=False)[numeric_cols]
        .mean()
        .round(4)
    )

    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.write("**Rata-rata Space Saving (%)**")
        st.bar_chart(avg_df.set_index("Algorithm")["Space Save (%)"])
        st.write("**Rata-rata Waktu Proses (detik)**")
        st.bar_chart(avg_df.set_index("Algorithm")["Time (s)"])
    with chart_cols[1]:
        st.write("**Rata-rata PSNR**")
        st.bar_chart(avg_df.set_index("Algorithm")["PSNR"])
        st.write("**Rata-rata SSIM**")
        st.line_chart(avg_df.set_index("Algorithm")["SSIM"])


def render_results(results, visuals, mode_label):
    if not results:
        st.info("Output hasil pengujian akan muncul setelah minimal 10 file diproses.")
        return

    df_results = pd.DataFrame(results)
    render_summary_metrics(df_results)
    st.divider()
    render_visual_outputs(visuals, mode_label)
    st.divider()
    render_table_outputs(df_results, mode_label)
    st.divider()
    render_chart_outputs(df_results)


st.sidebar.title("Panel Pengujian")
mode = st.sidebar.radio(
    "Pilih alur",
    ["Bandingkan 3 Algoritma", "Uji Satuan Algoritma"],
)

st.sidebar.divider()
uploaded_files = st.sidebar.file_uploader(
    "Upload minimal 10 file (HEIC/JPG/PNG)",
    type=["heic", "heif", "jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=f"files_{mode}",
)
file_count = len(uploaded_files) if uploaded_files else 0

if file_count >= 10:
    st.sidebar.success(f"{file_count} file siap diproses.")
else:
    st.sidebar.warning(f"Minimal 10 file. Saat ini: {file_count} file.")

st.sidebar.divider()

if mode == "Bandingkan 3 Algoritma":
    active_algorithms = list(ALGORITHM_OPTIONS.keys())
    st.sidebar.subheader("Parameter 3 Algoritma")
    hevc_quality = st.sidebar.slider("HEVC Quality", 1, 100, 20, key="compare_hevc")
    chroma_value = st.sidebar.selectbox("Chroma Format", ["4:2:0", "4:2:2", "4:4:4"], key="compare_chroma")
    color_count = st.sidebar.number_input("Jumlah Warna", 2, 256, 16, step=2, key="compare_color")
    total_jobs = file_count * 3
    run_label = "Proses Perbandingan 3 Algoritma"
    session_result_key = "compare_results"
    session_visual_key = "compare_visuals"
else:
    selected_algorithm = st.sidebar.selectbox("Pilih algoritma", list(ALGORITHM_OPTIONS.keys()))
    active_algorithms = [selected_algorithm]
    st.sidebar.subheader("Parameter Algoritma")
    hevc_quality = st.sidebar.slider("HEVC Quality", 1, 100, 20, key="single_hevc")
    chroma_value = st.sidebar.selectbox("Chroma Format", ["4:2:0", "4:2:2", "4:4:4"], key="single_chroma")
    color_count = st.sidebar.number_input("Jumlah Warna", 2, 256, 16, step=2, key="single_color")
    st.sidebar.caption(ALGORITHM_OPTIONS[selected_algorithm]["description"])
    total_jobs = file_count
    run_label = "Proses Algoritma Terpilih"
    session_result_key = "single_results"
    session_visual_key = "single_visuals"

st.sidebar.caption(
    f"Total pekerjaan: {file_count} file x {len(active_algorithms)} algoritma = {total_jobs} proses."
)

process_disabled = file_count < 10
run_process = st.sidebar.button(
    run_label,
    type="primary",
    disabled=process_disabled,
    use_container_width=True,
)

if st.sidebar.button("Bersihkan Hasil Mode Ini", use_container_width=True):
    st.session_state[session_result_key] = []
    st.session_state[session_visual_key] = []
    st.rerun()


st.markdown(
    """
    <div class="hero">
        <h1>HEIC Compression Lab</h1>
        <p>Upload minimal 10 file HEIC dari sidebar, pilih alur pengujian, lalu lihat output gambar, tabel, dan grafik secara berurutan.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if mode == "Bandingkan 3 Algoritma":
    st.header("Membandingkan Langsung 3 Algoritma")
    st.markdown(
        "<p class='muted'>Alur ini menjalankan HEVC Quality, Chroma Subsampling, dan Color Quantization untuk setiap file.</p>",
        unsafe_allow_html=True,
    )
else:
    st.header("Membandingkan Satuan Algoritma")
    st.markdown(
        f"<p class='muted'>Alur ini hanya menjalankan algoritma yang dipilih di sidebar: {active_algorithms[0]}.</p>",
        unsafe_allow_html=True,
    )

if file_count >= 10:
    st.markdown(
        f"<div class='status-ok'>{file_count} file sudah memenuhi syarat minimal 10. Klik tombol proses di sidebar untuk menampilkan hasil pengujian.</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<div class='status-warn'>Upload minimal 10 file HEIC agar output gambar, tabel, dan grafik bisa ditampilkan. Saat ini baru {file_count} file.</div>",
        unsafe_allow_html=True,
    )

if run_process:
    try:
        results, visuals = run_batch(
            uploaded_files,
            active_algorithms,
            hevc_quality,
            chroma_value,
            color_count,
            mode,
        )
        st.session_state[session_result_key] = results
        st.session_state[session_visual_key] = visuals
        st.session_state["history"].extend(results)
        st.success("Proses selesai. Output gambar, tabel, dan grafik sudah diperbarui.")
    except Exception as exc:
        st.error(f"Proses gagal: {exc}")

render_results(
    st.session_state[session_result_key],
    st.session_state[session_visual_key],
    "compare" if mode == "Bandingkan 3 Algoritma" else "single",
)
