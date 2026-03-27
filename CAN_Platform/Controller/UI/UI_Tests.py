import tkinter as tk
import math
import matplotlib.pyplot as plt

from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib.patches import Wedge, Rectangle


class RPMGaugeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RPM Gauge Simulation")
        self.root.geometry("1000x700")
        
        self.rpm = 0
        self.max_rpm = 8000
        
        # Create main frames
        gauge_frame = ttk.Frame(root)
        gauge_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(root)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create gauge
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=gauge_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        ttk.Label(control_frame, text="RPM Gauge Control", font=("Arial", 14, "bold")).pack(pady=10)
        
        ttk.Label(control_frame, text="Set RPM:").pack(pady=5)
        self.rpm_slider = ttk.Scale(control_frame, from_=0, to=self.max_rpm, 
                                     orient=tk.HORIZONTAL, command=self.update_rpm)
        self.rpm_slider.pack(fill=tk.X, padx=5)
        
        self.rpm_label = ttk.Label(control_frame, text="0 RPM", font=("Arial", 12))
        self.rpm_label.pack(pady=5)
        
        # Data table
        ttk.Label(control_frame, text="RPM History", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.tree = ttk.Treeview(control_frame, columns=("RPM", "Status"), height=10, show="headings")
        self.tree.column("RPM", width=80)
        self.tree.column("Status", width=100)
        self.tree.heading("RPM", text="RPM")
        self.tree.heading("Status", text="Status")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5)
        
        self.draw_gauge()
        
    def update_rpm(self, value):
        self.rpm = int(float(value))
        self.rpm_label.config(text=f"{self.rpm} RPM")
        self.draw_gauge()
        self.update_table()
        
    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        status = "Idle" if self.rpm < 1000 else "Normal" if self.rpm < 6000 else "High"
        self.tree.insert("", "end", values=(self.rpm, status))
        
    def draw_gauge(self):
        self.ax.clear()
        self.ax.set_xlim(-1.5, 1.5)
        self.ax.set_ylim(-0.5, 1.5)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        
        # Draw gauge background
        circle = plt.Circle((0, 0), 1, color="lightgray", ec="black", linewidth=2)
        self.ax.add_patch(circle)
        
        # Draw tick marks and labels
        for i in range(0, int(self.max_rpm) + 1000, 1000):
            angle = 225 - (i / self.max_rpm) * 270
            rad = math.radians(angle)
            x1, y1 = 0.9 * math.cos(rad), 0.9 * math.sin(rad)
            x2, y2 = 1.0 * math.cos(rad), 1.0 * math.sin(rad)
            self.ax.plot([x1, x2], [y1, y2], "k-", linewidth=2)
            
            x_text = 0.75 * math.cos(rad)
            y_text = 0.75 * math.sin(rad)
            self.ax.text(x_text, y_text, str(int(i/1000)), ha="center", va="center", fontsize=9)
        
        # Draw needle
        angle = 225 - (self.rpm / self.max_rpm) * 270
        rad = math.radians(angle)
        self.ax.arrow(0, 0, 0.7 * math.cos(rad), 0.7 * math.sin(rad),
                      head_width=0.1, head_length=0.1, fc="red", ec="red")
        
        # Center circle
        center = plt.Circle((0, 0), 0.08, color="black")
        self.ax.add_patch(center)
        
        self.ax.set_title("RPM Gauge", fontsize=14, fontweight="bold")
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = RPMGaugeApp(root)
    root.mainloop()