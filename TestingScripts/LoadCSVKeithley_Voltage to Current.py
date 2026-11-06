import os
import tkinter as tk
from tkinter import filedialog

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


print("Please select your data files")

# File selection dialog
root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

file_paths = filedialog.askopenfilenames(
    title="Select Current vs Time files",
    filetypes=[
        ("Supported data files", "*.xlsx *.xls *.csv *.pkl"),
        ("Excel files", "*.xlsx *.xls"),
        ("CSV files", "*.csv"),
        ("Pickle files", "*.pkl"),
    ],
)

root.destroy()

if not file_paths:
    print("No file selected")
    raise SystemExit

print("Selected files:", file_paths)

# Create output folder
base_folder = os.path.dirname(file_paths[0])
report_folder = os.path.join(base_folder, "reportsmerged")
os.makedirs(report_folder, exist_ok=True)

pdf_path = os.path.join(report_folder, "all_plots.pdf")

# Conversion factor: Voltage -> Current in nA
CONVERSION_FACTOR = 105

with PdfPages(pdf_path) as pdf:

    combined_fig, combined_ax = plt.subplots(figsize=(10, 6))

    combined_ax.set_title("Combined Current vs Time")
    combined_ax.set_xlabel("Time [s]")
    combined_ax.set_ylabel("Current [nA]")
    combined_ax.grid(True)

    for file_path in file_paths:

        ext = os.path.splitext(file_path)[1].lower()

        # Read file
        try:
            if ext in [".xlsx", ".xls"]:
                df = pd.read_excel(file_path)

            elif ext == ".csv":
                df = pd.read_csv(
                    file_path,
                    sep=",",
                    decimal=".",
                    skiprows=4,
                    names=["Time (s)", "Current"],
                )

            elif ext == ".pkl":
                df = pd.read_pickle(file_path)

            else:
                print(f"Unsupported file format: {file_path}")
                continue

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

        # Normalize column names
        df.columns = df.columns.astype(str).str.strip()

        # Check required columns
        if "Time (s)" not in df.columns or "Current" not in df.columns:
            print(f"Required columns not found in {file_path}")
            print("Available columns:", df.columns.tolist())
            continue

        # Convert columns to numeric
        df["Time (s)"] = pd.to_numeric(
            df["Time (s)"], errors="coerce"
        )
        df["Current"] = pd.to_numeric(
            df["Current"], errors="coerce"
        )

        # Remove invalid data
        df = df.dropna(subset=["Time (s)", "Current"])

        if df.empty:
            print(f"No valid data in {file_path}")
            continue

        # Extract time and voltage
        time = df["Time (s)"].to_numpy()
        voltage = df["Current"].to_numpy()

        # Convert voltage to current in nA
        current_nA = voltage * CONVERSION_FACTOR

        filename = os.path.basename(file_path)

        # Individual plot
        fig, ax = plt.subplots(figsize=(10, 6))

        ax.plot(time, current_nA)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("Current [nA]")
        ax.set_title(f"Current vs Time - {filename}")
        ax.grid(True)

        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        # Add to combined plot
        combined_ax.plot(
            time,
            current_nA,
            label=filename,
            alpha=0.7,
        )

        print(f"Processed: {filename}")

    combined_ax.legend()
    combined_fig.tight_layout()

    pdf.savefig(combined_fig)
    plt.close(combined_fig)

print(f"\nPDF report saved to: {pdf_path}")
