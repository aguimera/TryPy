import os
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nptdms import TdmsFile


print("Please select input method (Files or Folder)")

root = tk.Tk()
root.withdraw()
root.lift()
root.attributes("-topmost", True)

# Ask the user to select individual files or a folder
choice = messagebox.askyesno(
    "Select Input Type",
    "Do you want to select individual files?\n\n"
    "(Click 'Yes' for files, 'No' for a whole folder)"
)

tdms_paths = []
base_folder = None

if choice:
    # Select one or multiple TDMS files
    tdms_paths = list(
        filedialog.askopenfilenames(
            title="Select TDMS files",
            filetypes=[("TDMS files", "*.tdms")]
        )
    )

    if tdms_paths:
        base_folder = os.path.dirname(tdms_paths[0])

else:
    # Select a folder containing TDMS files
    folder_path = filedialog.askdirectory(
        title="Select Folder with TDMS files"
    )

    if folder_path:
        base_folder = folder_path
        tdms_paths = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(".tdms")
        ]

root.destroy()

# Check whether files were selected
if not tdms_paths:
    print("No files selected or no TDMS files found.")
    raise SystemExit

print(f"Found {len(tdms_paths)} TDMS files to process.")

# Create the report folder
report_folder = os.path.join(base_folder, "reportsmerged")

try:
    os.makedirs(report_folder, exist_ok=True)
    pdf_path = os.path.join(report_folder, "all_plots.pdf")

    # Test whether the PDF can be created
    with open(pdf_path, "wb"):
        pass

except Exception:
    print(
        "Warning: Cannot write to the selected folder. "
        "Saving to Desktop instead."
    )

    report_folder = os.path.join(
        os.path.expanduser("~"),
        "Desktop",
        "reportsmerged"
    )

    os.makedirs(report_folder, exist_ok=True)
    pdf_path = os.path.join(report_folder, "all_plots.pdf")


# Create the PDF report
with PdfPages(pdf_path) as pdf:

    # Combined plot
    combined_fig, combined_ax = plt.subplots(figsize=(10, 6))

    combined_ax.set_title("Combined Voltage vs Time")
    combined_ax.set_xlabel("Time [s]")
    combined_ax.set_ylabel("Voltage [V]")
    combined_ax.grid(True)

    # Process files in reverse order
    for file_path in reversed(tdms_paths):

        print(f"Processing: {os.path.basename(file_path)}")

        try:
            tdms_file = TdmsFile.read(file_path)

            # Find the first group containing channels
            group = next(
                (g for g in tdms_file.groups() if g.channels()),
                None
            )

            if group is None:
                print(f"No channels found in file: {file_path}")
                continue

            # Read the first channel
            channel = group.channels()[0]
            voltage = channel[:]

            # Calculate time from the sampling interval, if available
            dt = channel.properties.get("wf_increment", None)

            if dt is not None:
                time = np.arange(len(voltage)) * dt
                x_label = "Time [s]"
            else:
                time = np.arange(len(voltage))
                x_label = "Samples"

            # Create an individual plot
            fig, ax = plt.subplots(figsize=(10, 6))

            ax.plot(time, voltage)
            ax.set_xlabel(x_label)
            ax.set_ylabel("Voltage [V]")
            ax.set_ylim(-10, 10)  # Fixed voltage axis limits
            ax.set_title(
                f"Voltage vs Time - {os.path.basename(file_path)}"
            )
            ax.grid(True)

            # Save the individual plot to the PDF
            pdf.savefig(fig)
            plt.close(fig)

            # Add the signal to the combined plot
            combined_ax.plot(
                time,
                voltage,
                label=os.path.basename(file_path),
                alpha=0.7
            )

        except Exception as error:
            print(f"Error processing {file_path}: {error}")

    # Save the combined plot
    handles, labels = combined_ax.get_legend_handles_labels()

    if handles:
        combined_ax.legend(loc="upper right", fontsize="small")

    pdf.savefig(combined_fig)
    plt.close(combined_fig)

print(f"PDF report saved successfully: {pdf_path}")