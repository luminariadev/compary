import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
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

class MainWindow(ctk.CTkFrame):
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
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Load Image Button
        btn_load = ctk.CTkButton(control_frame, text="Load HEIC Image", command=self.load_image)
        btn_load.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_image_path = ctk.CTkLabel(control_frame, text="No image loaded")
        self.lbl_image_path.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Algorithm Selection
        lbl_algo = ctk.CTkLabel(control_frame, text="Algorithm:")
        lbl_algo.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.algo_var = ctk.StringVar(value="HEVC Quality")
        algo_cb = ctk.CTkComboBox(control_frame, variable=self.algo_var, values=["HEVC Quality", "Chroma Subsampling", "Color Quantization"], command=self.on_algo_change)
        algo_cb.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Parameters Frame (Dynamic)
        self.param_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        self.param_frame.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        self.setup_parameters()
        
        # Compress Button
        btn_compress = ctk.CTkButton(control_frame, text="Compress Image", command=self.run_compression, fg_color="#28a745", hover_color="#218838")
        btn_compress.grid(row=1, column=3, padx=20, pady=10)
        
        # Theme toggle
        self.theme_var = ctk.StringVar(value="System")
        theme_cb = ctk.CTkComboBox(control_frame, variable=self.theme_var, values=["System", "Light", "Dark"], command=self.change_theme)
        theme_cb.grid(row=0, column=3, padx=20, pady=10, sticky="e")
        
        # Middle Frame: Previews
        preview_frame = ctk.CTkFrame(self, fg_color="transparent")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Original Preview
        orig_frame = ctk.CTkFrame(preview_frame)
        orig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        lbl_orig_title = ctk.CTkLabel(orig_frame, text="Original Preview", font=ctk.CTkFont(weight="bold"))
        lbl_orig_title.pack(pady=5)
        self.lbl_orig_img = ctk.CTkLabel(orig_frame, text="")
        self.lbl_orig_img.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Compressed Preview
        comp_frame = ctk.CTkFrame(preview_frame)
        comp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        lbl_comp_title = ctk.CTkLabel(comp_frame, text="Compressed Preview", font=ctk.CTkFont(weight="bold"))
        lbl_comp_title.pack(pady=5)
        self.lbl_comp_img = ctk.CTkLabel(comp_frame, text="")
        self.lbl_comp_img.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bottom Frame: Metrics
        metrics_frame = ctk.CTkFrame(self)
        metrics_frame.pack(fill=tk.X, pady=10, padx=10)
        
        lbl_metrics_title = ctk.CTkLabel(metrics_frame, text="Metrics & Results (Latest Run)", font=ctk.CTkFont(weight="bold"))
        lbl_metrics_title.pack(pady=5)
        
        self.metrics_text = ctk.CTkTextbox(metrics_frame, height=100)
        self.metrics_text.pack(fill=tk.X, padx=10, pady=5)
        self.metrics_text.insert("0.0", "No data yet.\n")
        self.metrics_text.configure(state="disabled")
        
        btn_export = ctk.CTkButton(metrics_frame, text="Export All Results CSV", command=self.export_csv)
        btn_export.pack(pady=10)
        
    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

    def setup_parameters(self, *args):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        algo = self.algo_var.get()
        if algo == "HEVC Quality":
            ctk.CTkLabel(self.param_frame, text="Quality (1-100):").pack(side=tk.LEFT)
            self.param_val = ctk.StringVar(value="50")
            # Fallback to standard entry as CTk doesn't have a built-in Spinbox
            entry = ctk.CTkEntry(self.param_frame, textvariable=self.param_val, width=60)
            entry.pack(side=tk.LEFT, padx=10)
        elif algo == "Chroma Subsampling":
            ctk.CTkLabel(self.param_frame, text="Subsampling:").pack(side=tk.LEFT)
            self.param_val = ctk.StringVar(value="4:2:0")
            cb = ctk.CTkComboBox(self.param_frame, variable=self.param_val, values=["4:2:0", "4:2:2", "4:4:4"], width=100)
            cb.pack(side=tk.LEFT, padx=10)
        elif algo == "Color Quantization":
            ctk.CTkLabel(self.param_frame, text="Colors:").pack(side=tk.LEFT)
            self.param_val = ctk.StringVar(value="16")
            entry = ctk.CTkEntry(self.param_frame, textvariable=self.param_val, width=60)
            entry.pack(side=tk.LEFT, padx=10)

    def on_algo_change(self, choice):
        self.setup_parameters()
        
    def load_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("HEIC Files", "*.heic;*.HEIC")])
        if filepath:
            self.original_image_path = filepath
            self.lbl_image_path.configure(text=os.path.basename(filepath))
            
            # Load with pillow
            self.original_img_pil = Image.open(filepath).convert("RGB")
            self.original_img_np = np.array(self.original_img_pil)
            
            # Display Original
            self.display_image(self.original_img_pil, self.lbl_orig_img)
            # Clear compressed
            self.lbl_comp_img.configure(image=None, text="")
            
    def display_image(self, img_pil, label_widget):
        # Resize for preview
        img_copy = img_pil.copy()
        img_copy.thumbnail((400, 400))
        
        # ctk handles PIL images nicely if we use CTkImage
        ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img # Keep reference
        
    def run_compression(self):
        if not self.original_image_path:
            messagebox.showerror("Error", "Please load an image first!")
            return
            
        algo = self.algo_var.get()
        param = self.param_val.get()
        
        # Create temp output path
        temp_dir = tempfile.gettempdir()
        self.compressed_image_path = os.path.join(temp_dir, f"compressed_{int(time.time())}.heic")
        
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
            
            # Update Metrics Textbox
            result_str = (
                f"Algorithm: {algo} | Parameter: {param} | Time: {time_taken:.2f} s\n"
                f"Size: {comp_metrics['Original Size (bytes)']/1024:.2f} KB -> {comp_metrics['Compressed Size (bytes)']/1024:.2f} KB | "
                f"Ratio: {comp_metrics['Compression Ratio']} | Space Savings: {comp_metrics['Space Savings (%)']}%\n"
                f"BPP: {comp_metrics['BPP']} | PSNR: {qual_metrics['PSNR']} | SSIM: {qual_metrics['SSIM']} | MSE: {qual_metrics['MSE']}\n"
            )
            
            self.metrics_text.configure(state="normal")
            self.metrics_text.delete("0.0", "end")
            self.metrics_text.insert("0.0", result_str)
            self.metrics_text.configure(state="disabled")
            
            row_data = (
                algo, param, round(time_taken, 2),
                comp_metrics["Original Size (bytes)"], comp_metrics["Compressed Size (bytes)"],
                comp_metrics["Compression Ratio"], comp_metrics["Space Savings (%)"],
                comp_metrics["BPP"],
                qual_metrics["PSNR"], qual_metrics["SSIM"], qual_metrics["MSE"]
            )
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
