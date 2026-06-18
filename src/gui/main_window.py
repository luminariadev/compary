import customtkinter as ctk
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

class MainWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.original_image_path = None
        
        self.results_data = [] # To store metrics for export
        
        # Style for Treeview to make it look good in light/dark mode
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", background="#f0f0f0", foreground="black", rowheight=25, fieldbackground="#f0f0f0")
        style.map('Treeview', background=[('selected', '#0078D7')])
        style.configure("Treeview.Heading", background="#d9d9d9", foreground="black", font=('Helvetica', 10, 'bold'))
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Top Frame: General Controls (Theme, Export)
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill=tk.X, pady=5)
        
        self.theme_var = ctk.StringVar(value="System")
        theme_cb = ctk.CTkComboBox(top_bar, variable=self.theme_var, values=["System", "Light", "Dark"], command=self.change_theme)
        theme_cb.pack(side=tk.RIGHT, padx=5)
        ctk.CTkLabel(top_bar, text="Theme:").pack(side=tk.RIGHT, padx=5)
        
        # Tab View
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tab_single = self.tabview.add("Single Algorithm")
        self.tab_compare = self.tabview.add("Compare 3 Algorithms")
        
        self._setup_single_tab()
        self._setup_compare_tab()
        
        # Bottom Frame: Metrics Table (Global for both tabs)
        metrics_frame = ctk.CTkFrame(self)
        metrics_frame.pack(fill=tk.X, pady=10)
        
        lbl_metrics_title = ctk.CTkLabel(metrics_frame, text="Metrics & Results History", font=ctk.CTkFont(weight="bold"))
        lbl_metrics_title.pack(pady=5)
        
        columns = ("Algorithm", "Param", "Time (s)", "Orig Size", "Comp Size", "Ratio", "Space Save%", "BPP", "PSNR", "SSIM", "MSE")
        self.tree = ttk.Treeview(metrics_frame, columns=columns, show="headings", height=6)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)
        self.tree.pack(fill=tk.X, padx=10, pady=5)
        
        btn_export = ctk.CTkButton(metrics_frame, text="Export All Results CSV", command=self.export_csv)
        btn_export.pack(pady=10)
        
    def _setup_single_tab(self):
        control_frame = ctk.CTkFrame(self.tab_single)
        control_frame.pack(fill=tk.X, pady=5)
        
        # Load Image Button
        btn_load = ctk.CTkButton(control_frame, text="Load HEIC Image", command=self.load_image_single)
        btn_load.grid(row=0, column=0, padx=10, pady=10)
        self.lbl_image_path_single = ctk.CTkLabel(control_frame, text="No image loaded")
        self.lbl_image_path_single.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
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
        btn_compress = ctk.CTkButton(control_frame, text="Compress Image", command=self.run_compression_single, fg_color="#28a745", hover_color="#218838")
        btn_compress.grid(row=1, column=3, padx=20, pady=10)
        
        # Previews
        preview_frame = ctk.CTkFrame(self.tab_single, fg_color="transparent")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        orig_frame = ctk.CTkFrame(preview_frame)
        orig_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        ctk.CTkLabel(orig_frame, text="Original Preview", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.lbl_orig_img_single = ctk.CTkLabel(orig_frame, text="")
        self.lbl_orig_img_single.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        comp_frame = ctk.CTkFrame(preview_frame)
        comp_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        ctk.CTkLabel(comp_frame, text="Compressed Preview", font=ctk.CTkFont(weight="bold")).pack(pady=5)
        self.lbl_comp_img_single = ctk.CTkLabel(comp_frame, text="")
        self.lbl_comp_img_single.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _setup_compare_tab(self):
        control_frame = ctk.CTkFrame(self.tab_compare)
        control_frame.pack(fill=tk.X, pady=5)
        
        btn_load = ctk.CTkButton(control_frame, text="Load HEIC Image", command=self.load_image_compare)
        btn_load.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.lbl_image_path_comp = ctk.CTkLabel(control_frame, text="No image loaded")
        self.lbl_image_path_comp.pack(side=tk.LEFT, padx=10, pady=10)
        
        btn_run_all = ctk.CTkButton(control_frame, text="Run All 3 Algorithms", command=self.run_compression_compare, fg_color="#007bff", hover_color="#0056b3")
        btn_run_all.pack(side=tk.RIGHT, padx=10, pady=10)
        
        # Params row
        param_row = ctk.CTkFrame(self.tab_compare, fg_color="transparent")
        param_row.pack(fill=tk.X, pady=5)
        
        self.comp_hevc_var = ctk.StringVar(value="50")
        self.comp_chroma_var = ctk.StringVar(value="4:2:0")
        self.comp_color_var = ctk.StringVar(value="16")
        
        f1 = ctk.CTkFrame(param_row)
        f1.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ctk.CTkLabel(f1, text="HEVC Quality:").pack(side=tk.LEFT, padx=5)
        ctk.CTkEntry(f1, textvariable=self.comp_hevc_var, width=60).pack(side=tk.LEFT, padx=5)
        
        f2 = ctk.CTkFrame(param_row)
        f2.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ctk.CTkLabel(f2, text="Chroma Subsampling:").pack(side=tk.LEFT, padx=5)
        ctk.CTkComboBox(f2, variable=self.comp_chroma_var, values=["4:2:0", "4:2:2", "4:4:4"], width=80).pack(side=tk.LEFT, padx=5)
        
        f3 = ctk.CTkFrame(param_row)
        f3.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        ctk.CTkLabel(f3, text="Color Quantization:").pack(side=tk.LEFT, padx=5)
        ctk.CTkEntry(f3, textvariable=self.comp_color_var, width=60).pack(side=tk.LEFT, padx=5)
        
        # Previews
        preview_frame = ctk.CTkFrame(self.tab_compare, fg_color="transparent")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 3 columns for 3 algorithms
        self.lbl_comp_algo1 = self._create_preview_col(preview_frame, "HEVC Quality")
        self.lbl_comp_algo2 = self._create_preview_col(preview_frame, "Chroma Subsampling")
        self.lbl_comp_algo3 = self._create_preview_col(preview_frame, "Color Quantization")

    def _create_preview_col(self, parent, title):
        frame = ctk.CTkFrame(parent)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(weight="bold")).pack(pady=5)
        lbl = ctk.CTkLabel(frame, text="")
        lbl.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return lbl

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)
        # Update Treeview style
        style = ttk.Style()
        if choice == "Dark":
            style.configure("Treeview", background="#2b2b2b", foreground="white", fieldbackground="#2b2b2b")
            style.configure("Treeview.Heading", background="#404040", foreground="white")
        else: # Light or System (assumed light)
            style.configure("Treeview", background="#f0f0f0", foreground="black", fieldbackground="#f0f0f0")
            style.configure("Treeview.Heading", background="#d9d9d9", foreground="black")

    def setup_parameters(self, *args):
        for widget in self.param_frame.winfo_children():
            widget.destroy()
            
        algo = self.algo_var.get()
        if algo == "HEVC Quality":
            ctk.CTkLabel(self.param_frame, text="Quality (1-100):").pack(side=tk.LEFT)
            self.param_val_single = ctk.StringVar(value="50")
            ctk.CTkEntry(self.param_frame, textvariable=self.param_val_single, width=60).pack(side=tk.LEFT, padx=10)
        elif algo == "Chroma Subsampling":
            ctk.CTkLabel(self.param_frame, text="Subsampling:").pack(side=tk.LEFT)
            self.param_val_single = ctk.StringVar(value="4:2:0")
            ctk.CTkComboBox(self.param_frame, variable=self.param_val_single, values=["4:2:0", "4:2:2", "4:4:4"], width=100).pack(side=tk.LEFT, padx=10)
        elif algo == "Color Quantization":
            ctk.CTkLabel(self.param_frame, text="Colors:").pack(side=tk.LEFT)
            self.param_val_single = ctk.StringVar(value="16")
            ctk.CTkEntry(self.param_frame, textvariable=self.param_val_single, width=60).pack(side=tk.LEFT, padx=10)

    def on_algo_change(self, choice):
        self.setup_parameters()
        
    def _load_image_logic(self):
        filepath = filedialog.askopenfilename(filetypes=[("HEIC Files", "*.heic;*.HEIC")])
        if filepath:
            self.original_image_path = filepath
            # Load with pillow
            self.original_img_pil = Image.open(filepath).convert("RGB")
            self.original_img_np = np.array(self.original_img_pil)
            return filepath
        return None

    def load_image_single(self):
        fp = self._load_image_logic()
        if fp:
            self.lbl_image_path_single.configure(text=os.path.basename(fp))
            self.display_image(self.original_img_pil, self.lbl_orig_img_single)
            self.lbl_comp_img_single.configure(image=None, text="")

    def load_image_compare(self):
        fp = self._load_image_logic()
        if fp:
            self.lbl_image_path_comp.configure(text=os.path.basename(fp))
            # Clear previews
            for lbl in [self.lbl_comp_algo1, self.lbl_comp_algo2, self.lbl_comp_algo3]:
                lbl.configure(image=None, text="")
            
    def display_image(self, img_pil, label_widget):
        img_copy = img_pil.copy()
        img_copy.thumbnail((300, 300)) # Smaller for 3 cols
        ctk_img = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img
        
    def _run_algo_logic(self, algo, param, label_widget=None):
        temp_dir = tempfile.gettempdir()
        comp_path = os.path.join(temp_dir, f"compressed_{int(time.time()*1000)}.heic")
        
        time_taken = 0
        if algo == "HEVC Quality":
            time_taken = compress_hevc_quality(self.original_image_path, comp_path, int(param))
        elif algo == "Chroma Subsampling":
            time_taken = compress_chroma_subsampling(self.original_image_path, comp_path, param)
        elif algo == "Color Quantization":
            time_taken = compress_color_quantization(self.original_image_path, comp_path, int(param))
            
        comp_pil = Image.open(comp_path).convert("RGB")
        comp_np = np.array(comp_pil)
        
        if label_widget:
            self.display_image(comp_pil, label_widget)
            
        comp_metrics = calculate_compression_metrics(self.original_image_path, comp_path, self.original_img_np)
        qual_metrics = calculate_quality_metrics(self.original_img_np, comp_np)
        
        row_data = (
            algo, param, round(time_taken, 2),
            comp_metrics["Original Size (bytes)"], comp_metrics["Compressed Size (bytes)"],
            comp_metrics["Compression Ratio"], comp_metrics["Space Savings (%)"],
            comp_metrics["BPP"],
            qual_metrics["PSNR"], qual_metrics["SSIM"], qual_metrics["MSE"]
        )
        self.tree.insert("", "end", values=row_data)
        self.results_data.append(row_data)

    def run_compression_single(self):
        if not self.original_image_path:
            messagebox.showerror("Error", "Please load an image first!")
            return
            
        self.parent.config(cursor="wait")
        self.update()
        try:
            algo = self.algo_var.get()
            param = self.param_val_single.get()
            self._run_algo_logic(algo, param, self.lbl_comp_img_single)
        except Exception as e:
            messagebox.showerror("Error", f"Compression failed: {str(e)}")
        finally:
            self.parent.config(cursor="")

    def run_compression_compare(self):
        if not self.original_image_path:
            messagebox.showerror("Error", "Please load an image first!")
            return
            
        self.parent.config(cursor="wait")
        self.update()
        try:
            # HEVC
            self._run_algo_logic("HEVC Quality", self.comp_hevc_var.get(), self.lbl_comp_algo1)
            # Chroma
            self._run_algo_logic("Chroma Subsampling", self.comp_chroma_var.get(), self.lbl_comp_algo2)
            # Color
            self._run_algo_logic("Color Quantization", self.comp_color_var.get(), self.lbl_comp_algo3)
            
            messagebox.showinfo("Success", "Komparasi selesai! Cek tabel metrik di bawah.")
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
