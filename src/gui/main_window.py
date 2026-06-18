import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
import tempfile
import csv
import time

from src.algorithms.hevc_quality import compress_hevc_quality
from src.algorithms.chroma_subsampling import compress_chroma_subsampling
from src.algorithms.color_quantization import compress_color_quantization
from src.metrics.quality_metrics import calculate_quality_metrics
from src.metrics.compression_metrics import calculate_compression_metrics

class MainWindow(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.original_image_path = None
        self.compressed_image_path = None
        self.original_img_pil = None
        self.compressed_img_pil = None
        self.original_img_np = None
        
        self.results_data = [] # To store metrics for export
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Top Frame: Controls
        control_frame = ttk.LabelFrame(self, text="Controls")
        control_frame.pack(fill=tk.X, pady=5)
        
        # Load Image Button
        ttk.Button(control_frame, text="Load HEIC Image", command=self.load_image).grid(row=0, column=0, padx=5, pady=5)
        self.lbl_image_path = ttk.Label(control_frame, text="No image loaded")
        self.lbl_image_path.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Algorithm Selection
        ttk.Label(control_frame, text="Algorithm:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        self.algo_var = tk.StringVar(value="HEVC Quality")
        algo_cb = ttk.Combobox(control_frame, textvariable=self.algo_var, values=["HEVC Quality", "Chroma Subsampling", "Color Quantization"], state="readonly")
        algo_cb.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        algo_cb.bind("<<ComboboxSelected>>", self.on_algo_change)
        
        # Parameters Frame (Dynamic)
        self.param_frame = ttk.Frame(control_frame)
        self.param_frame.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)
        self.setup_parameters()
        
        # Compress Button
        ttk.Button(control_frame, text="Compress Image", command=self.run_compression).grid(row=1, column=3, padx=20, pady=5)
        
        # Middle Frame: Previews
        preview_frame = ttk.Frame(self)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Original Preview
        orig_frame = ttk.LabelFrame(preview_frame, text="Original Preview")
        orig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_orig_img = ttk.Label(orig_frame)
        self.lbl_orig_img.pack(fill=tk.BOTH, expand=True)
        
        # Compressed Preview
        comp_frame = ttk.LabelFrame(preview_frame, text="Compressed Preview")
        comp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.lbl_comp_img = ttk.Label(comp_frame)
        self.lbl_comp_img.pack(fill=tk.BOTH, expand=True)
        
        # Bottom Frame: Metrics
        metrics_frame = ttk.LabelFrame(self, text="Metrics & Results")
        metrics_frame.pack(fill=tk.X, pady=5)
        
        columns = ("Algorithm", "Param", "Time (s)", "Orig Size", "Comp Size", "Ratio", "Space Save%", "BPP", "PSNR", "SSIM", "MSE")
        self.tree = ttk.Treeview(metrics_frame, columns=columns, show="headings", height=5)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(metrics_frame, text="Export Results CSV", command=self.export_csv).pack(pady=5)
        
    def setup_parameters(self):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        algo = self.algo_var.get()
        if algo == "HEVC Quality":
            ttk.Label(self.param_frame, text="Quality (1-100):").pack(side=tk.LEFT)
            self.param_val = tk.IntVar(value=50)
            ttk.Spinbox(self.param_frame, from_=1, to=100, textvariable=self.param_val, width=5).pack(side=tk.LEFT, padx=5)
        elif algo == "Chroma Subsampling":
            ttk.Label(self.param_frame, text="Subsampling:").pack(side=tk.LEFT)
            self.param_val = tk.StringVar(value="4:2:0")
            ttk.Combobox(self.param_frame, textvariable=self.param_val, values=["4:2:0", "4:2:2", "4:4:4"], width=8, state="readonly").pack(side=tk.LEFT, padx=5)
        elif algo == "Color Quantization":
            ttk.Label(self.param_frame, text="Colors:").pack(side=tk.LEFT)
            self.param_val = tk.IntVar(value=16)
            ttk.Spinbox(self.param_frame, from_=2, to=256, textvariable=self.param_val, width=5).pack(side=tk.LEFT, padx=5)

    def on_algo_change(self, event):
        self.setup_parameters()
        
    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("HEIC Files", "*.heic;*.HEIC")])
        if filepath:
            self.original_image_path = filepath
            self.lbl_image_path.config(text=os.path.basename(filepath))
            
            # Load with pillow
            self.original_img_pil = Image.open(filepath).convert("RGB")
            self.original_img_np = np.array(self.original_img_pil)
            
            # Display Original
            self.display_image(self.original_img_pil, self.lbl_orig_img)
            # Clear compressed
            self.lbl_comp_img.config(image='')
            
    def display_image(self, img_pil, label_widget):
        # Resize for preview
        img_copy = img_pil.copy()
        img_copy.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(img_copy)
        label_widget.config(image=photo)
        label_widget.image = photo # Keep reference
        
    def run_compression(self):
        if not self.original_image_path:
            messagebox.showerror("Error", "Please load an image first!")
            return
            
        algo = self.algo_var.get()
        param = self.param_val.get()
        
        # Create temp output path
        temp_dir = tempfile.gettempdir()
        self.compressed_image_path = os.path.join(temp_dir, f"compressed_{int(time.time())}.heic")
        
        # Disable button during processing
        # Show busy cursor
        self.parent.config(cursor="wait")
        self.update()
        
        try:
            time_taken = 0
            if algo == "HEVC Quality":
                time_taken = compress_hevc_quality(self.original_image_path, self.compressed_image_path, int(param))
            elif algo == "Chroma Subsampling":
                time_taken = compress_chroma_subsampling(self.original_image_path, self.compressed_image_path, param)
            elif algo == "Color Quantization":
                time_taken = compress_color_quantization(self.original_image_path, self.compressed_image_path, int(param))
                
            # Load compressed image for preview and metrics
            self.compressed_img_pil = Image.open(self.compressed_image_path).convert("RGB")
            compressed_img_np = np.array(self.compressed_img_pil)
            
            self.display_image(self.compressed_img_pil, self.lbl_comp_img)
            
            # Calculate Metrics
            comp_metrics = calculate_compression_metrics(self.original_image_path, self.compressed_image_path, self.original_img_np)
            qual_metrics = calculate_quality_metrics(self.original_img_np, compressed_img_np)
            
            # Insert to Treeview
            row_data = (
                algo, param, round(time_taken, 2),
                comp_metrics["Original Size (bytes)"], comp_metrics["Compressed Size (bytes)"],
                comp_metrics["Compression Ratio"], comp_metrics["Space Savings (%)"],
                comp_metrics["BPP"],
                qual_metrics["PSNR"], qual_metrics["SSIM"], qual_metrics["MSE"]
            )
            self.tree.insert("", "end", values=row_data)
            self.results_data.append(row_data)
            
        except Exception as e:
            messagebox.showerror("Error", f"Compression failed: {str(e)}")
        finally:
            self.parent.config(cursor="")
            
    def export_csv(self):
        if not self.results_data:
            messagebox.showinfo("Info", "No results to export.")
            return
            
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if filepath:
            with open(filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Algorithm", "Param", "Time (s)", "Orig Size", "Comp Size", "Ratio", "Space Save%", "BPP", "PSNR", "SSIM", "MSE"])
                writer.writerows(self.results_data)
            messagebox.showinfo("Success", "Results exported successfully.")
