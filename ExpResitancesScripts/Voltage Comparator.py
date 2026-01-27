import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
from matplotlib.backends.backend_pdf import PdfPages


print("Please provide file location")

root = tk.Tk()
root.withdraw()
root.lift()
root.attributes('-topmost', True)

DaqFiles = filedialog.askopenfilenames(
    title="Select Raw Data File/Files",
    filetypes=[("tdms files", "*.tdms")]
)

DAQColumnRenames = {
    'DMM-1 Time (s)': 'Time(s)',
    'DMM-1 Charge (C)': 'Charge(C)',
    'Index': 'Index',
}

# Base directory from first selected file
base_dir = os.path.dirname(DaqFiles[0])

# Reports folder
reports_dir = os.path.join(base_dir, "reports")
os.makedirs(reports_dir, exist_ok=True)

# PDF path
pdf_path = os.path.join(reports_dir, "Voltage_Analysis_Report.pdf")
# ========= CREATE PDF =========

with PdfPages(pdf_path) as pdf:

    # ========= OVERLAPPED FIGURE =========
    fig_all, ax_all = plt.subplots(figsize=(9,6))

    for file in DaqFiles:

        base_name = os.path.splitext(os.path.basename(file))[0]

        dfDAQ = pd.read_csv(
            file,
            header=16,
            index_col=False,
            delimiter=',',
            decimal=','
        )

        dfDAQ = dfDAQ.rename(columns=DAQColumnRenames)
        dfDAQ = dfDAQ.iloc[:-5]

        Time_float = np.array(
            [float(t.replace(',', '.')) for t in dfDAQ['Time(s)']]
        )
        Charge_float = np.array(
            [float(c.replace(',', '.')) for c in dfDAQ['Charge(C)']]
        )

        # --- derivative + smoothing ---
        Charge_dif = np.diff(Charge_float)
        window = 5
        Charge_diff_filtered = np.convolve(
            Charge_dif, np.ones(window)/window, mode='same'
        )

        # --- find active region ---
        start_idx = 0
        end_idx = 0
        max_charge = np.max(Charge_diff_filtered)

        for i in range(len(Charge_diff_filtered)):
            if Charge_diff_filtered[i] > max_charge * 0.5:
                if start_idx == 0:
                    start_idx = i
                end_idx = i

        time_mid = Time_float[start_idx:end_idx]
        charge_mid = Charge_float[start_idx:end_idx]

        # --- linear fit ---
        slope, intercept, *_ = linregress(time_mid, charge_mid)
        print(f"{base_name} → slope = {slope:.3e}")

        # =========================
        # INDIVIDUAL FIGURE (PDF PAGE)
        # =========================
        fig, ax = plt.subplots(figsize=(8,5))

        ax.plot(Time_float, Charge_float, alpha=0.6, label="Full Data")
        ax.plot(time_mid, charge_mid, 'o', color='orange', label="Fit region")
        ax.plot(
            time_mid,
            intercept + slope*time_mid,
            'r--',
            label=fr"Slope = {slope:.3e}"
        )

        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Charge (C)")
        ax.set_title(base_name)
        ax.legend()
        ax.grid(True)

        pdf.savefig(fig)
        plt.close(fig)

        # =========================
        # ADD TO OVERLAPPED FIGURE
        # =========================
        ax_all.plot(Time_float, Charge_float, alpha=0.4)
        ax_all.plot(
            time_mid,
            intercept + slope*time_mid,
            linewidth=2,
            label=f"{base_name} | slope={slope:.2e}"
        )

    # ========= FINAL OVERLAPPED PAGE =========
    ax_all.set_xlabel("Time (s)")
    ax_all.set_ylabel("Charge (C)")
    ax_all.set_title("Overlapped Charge Curves with Linear Fits")
    ax_all.legend(fontsize=9)
    ax_all.grid(True)

    pdf.savefig(fig_all)
    plt.close(fig_all)

print(f"\nPDF report saved as: {pdf_path}")