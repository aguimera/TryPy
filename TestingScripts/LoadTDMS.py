import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nptdms import TdmsFile
import numpy as np
import os

print("Please provide a file location")

root = tk.Tk()
root.withdraw()
root.lift()
root.attributes('-topmost', True)

tdms_paths = filedialog.askopenfilenames(
    title="Select TDMS files",
    filetypes=[("TDMS files", "*.tdms")]
)

if not tdms_paths:
    print("No file selected")
    exit()

print("Selected files:", tdms_paths)

base_folder = os.path.dirname(tdms_paths[0])
report_folder = os.path.join(base_folder, "reportsmerged")
os.makedirs(report_folder, exist_ok=True)

pdf_path = os.path.join(report_folder, "all_plots.pdf")

with PdfPages(pdf_path) as pdf:

    combined_fig = plt.figure(figsize=(10, 6))
    combined_ax = combined_fig.add_subplot(111)
    combined_ax.set_title("Combined Voltage vs Time")
    combined_ax.set_xlabel("Time [s]")
    combined_ax.set_ylabel("Voltage [V]")
    combined_ax.grid(True)

    for file_path in reversed(tdms_paths):
        tdms_file = TdmsFile.read(file_path)

        group = next((g for g in tdms_file.groups() if g.channels()), None)
        if group is None:
            print(f"No channels found in file: {file_path}")
            continue

        channel = group.channels()[0]
        voltage = channel[:]

        dt = channel.properties.get("wf_increment", None)
        time = np.arange(len(voltage)) * dt if dt is not None else np.arange(len(voltage))

        # Individual plot
        fig, ax = plt.subplots(figsize=(10, 6))
        mid_index = len(time) -12998
        ax.plot(time[mid_index:], voltage[mid_index:])
        ax.set_xlabel("Time [s]" if dt else "Samples")
        ax.set_ylabel("Voltage [V]")
        ax.set_title(f"Voltage vs Time - {os.path.basename(file_path)}")
        ax.grid(True)

        pdf.savefig(fig)
        plt.close(fig)

        # Add to combined plot with transparency
        combined_ax.plot(time[mid_index:], voltage[mid_index:], label=os.path.basename(file_path), alpha=0.7)
    combined_ax.legend()
    pdf.savefig(combined_fig)
    plt.close(combined_fig)

print(f"Saved PDF: {pdf_path}")
