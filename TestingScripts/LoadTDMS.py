import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from nptdms import TdmsFile


# ============================================================
# SETTINGS
# ============================================================

# Fixed voltage display range for every plot
VOLTAGE_MIN = -10.0
VOLTAGE_MAX = 10.0

# Set True to search selected folder and all its subfolders
SEARCH_SUBFOLDERS = False

# PDF output filename
PDF_FILENAME = "raw_voltage_report.pdf"

# Figure size
FIGURE_SIZE = (12, 6)

# PDF resolution
PDF_DPI = 200


# ============================================================
# SELECT TDMS FILES OR A FOLDER
# ============================================================

def select_tdms_files():

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    select_files = messagebox.askyesno(
        "Select input",
        "Do you want to select individual TDMS files?\n\n"
        "Yes: select one or more TDMS files\n"
        "No: select a folder containing TDMS files"
    )

    tdms_paths = []

    if select_files:

        tdms_paths = list(
            filedialog.askopenfilenames(
                title="Select TDMS files",
                filetypes=[("TDMS files", "*.tdms")]
            )
        )

        output_base = (
            os.path.dirname(tdms_paths[0])
            if tdms_paths else None
        )

    else:

        folder = filedialog.askdirectory(
            title="Select folder containing TDMS files"
        )

        output_base = folder or None

        if folder:

            if SEARCH_SUBFOLDERS:

                for current_folder, _, filenames in os.walk(folder):

                    for filename in filenames:

                        if filename.lower().endswith(".tdms"):

                            tdms_paths.append(
                                os.path.join(
                                    current_folder,
                                    filename
                                )
                            )

            else:

                tdms_paths = [
                    os.path.join(folder, filename)
                    for filename in os.listdir(folder)
                    if filename.lower().endswith(".tdms")
                ]

    root.destroy()

    return sorted(tdms_paths), output_base


# ============================================================
# GET TIME AXIS
# ============================================================

def get_time_axis(channel, number_of_samples):

    """
    Use TDMS waveform timing metadata when available.
    Otherwise, use sample number.
    """

    properties = channel.properties

    dt = properties.get("wf_increment")

    start_time = properties.get(
        "wf_start_offset",
        0.0
    )

    if dt is not None:

        time = (
            float(start_time)
            + np.arange(number_of_samples) * float(dt)
        )

        return time, "Time [s]", float(dt)

    return np.arange(number_of_samples), "Sample", None


# ============================================================
# ADD ONE CHANNEL PLOT TO THE PDF
# ============================================================

def add_channel_plot(
    pdf,
    filename,
    group_name,
    channel,
    voltage
):

    time, x_label, dt = get_time_axis(
        channel,
        len(voltage)
    )

    # Create figure

    fig, ax = plt.subplots(
        figsize=FIGURE_SIZE
    )

    # Plot raw voltage

    ax.plot(
        time,
        voltage,
        linewidth=0.7,
        color="tab:blue",
        label="Raw voltage"
    )

    # Fixed voltage scale

    ax.set_ylim(
        VOLTAGE_MIN,
        VOLTAGE_MAX
    )

    # Labels

    ax.set_xlabel(x_label)

    ax.set_ylabel("Voltage [V]")

    ax.set_title(
        f"Raw Voltage - {filename}\n"
        f"Group: {group_name} | "
        f"Channel: {channel.name}"
    )

    ax.grid(True, alpha=0.35)

    ax.legend(loc="upper right")

    # --------------------------------------------------------
    # MEASUREMENT INFORMATION
    # --------------------------------------------------------

    details = [
        f"Samples: {len(voltage):,}",
        f"Minimum measured voltage: {np.nanmin(voltage):.6g} V",
        f"Maximum measured voltage: {np.nanmax(voltage):.6g} V"
    ]

    if dt is not None:

        details.append(
            f"Sampling interval: {dt:.6g} s"
        )

        details.append(
            f"Sampling frequency: {1.0 / dt:.6g} Hz"
        )

        details.append(
            f"Record duration: {(len(voltage) - 1) * dt:.6g} s"
        )

    else:

        details.append(
            "Sampling interval: not available in TDMS metadata"
        )

    fig.text(
        0.08,
        0.025,
        " | ".join(details),
        ha="left",
        va="bottom",
        fontsize=8
    )

    # Adjust layout

    fig.tight_layout(
        rect=(0, 0.07, 1, 1)
    )

    # Save current plot as one PDF page

    pdf.savefig(
        fig,
        dpi=PDF_DPI
    )

    # Close figure to save memory

    plt.close(fig)


# ============================================================
# MAIN
# ============================================================

def main():

    # --------------------------------------------------------
    # SELECT INPUT FILES
    # --------------------------------------------------------

    tdms_paths, output_base = select_tdms_files()

    if not tdms_paths:

        print("No TDMS files selected or found.")

        return

    if not output_base:

        print("No output location available.")

        return

    # --------------------------------------------------------
    # CREATE OUTPUT FOLDER
    # --------------------------------------------------------

    output_folder = os.path.join(
        output_base,
        "raw_voltage_report"
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )

    pdf_path = os.path.join(
        output_folder,
        PDF_FILENAME
    )

    total_plots = 0

    failed_files = 0

    print(
        f"Found {len(tdms_paths)} TDMS file(s)."
    )

    print(
        f"PDF report: {pdf_path}"
    )

    # --------------------------------------------------------
    # CREATE PDF REPORT
    # --------------------------------------------------------

    with PdfPages(pdf_path) as pdf:

        # Process every TDMS file

        for file_path in tdms_paths:

            filename = os.path.basename(file_path)

            print(
                f"\nProcessing: {filename}"
            )

            try:

                # Read TDMS file

                tdms_file = TdmsFile.read(
                    file_path
                )

                # Process all groups

                for group in tdms_file.groups():

                    # Process all channels

                    for channel in group.channels():

                        try:

                            # --------------------------------
                            # READ RAW VOLTAGE
                            # --------------------------------

                            voltage = np.asarray(
                                channel[:],
                                dtype=float
                            )

                            if voltage.size == 0:

                                print(
                                    f"Empty channel '{channel.name}'. "
                                    "Skipping."
                                )

                                continue

                            # --------------------------------
                            # ADD PLOT TO PDF
                            # --------------------------------

                            add_channel_plot(
                                pdf=pdf,
                                filename=filename,
                                group_name=group.name,
                                channel=channel,
                                voltage=voltage
                            )

                            total_plots += 1

                            print(
                                f"Added page {total_plots}: "
                                f"{group.name}/{channel.name}"
                            )

                        except Exception as error:

                            print(
                                f"Error processing channel "
                                f"'{channel.name}': {error}"
                            )

            except Exception as error:

                failed_files += 1

                print(
                    f"Error reading {filename}: {error}"
                )

    # ========================================================
    # FINISHED
    # ========================================================

    print("\n====================================")

    print("TDMS PROCESSING FINISHED")

    print("====================================")

    print(
        f"TDMS files selected: {len(tdms_paths)}"
    )

    print(
        f"Plots added to PDF: {total_plots}"
    )

    print(
        f"Files with read errors: {failed_files}"
    )

    print(
        f"Voltage display range: "
        f"{VOLTAGE_MIN} V to +{VOLTAGE_MAX} V"
    )

    print(
        f"PDF report: {pdf_path}"
    )

    print("====================================")

    # --------------------------------------------------------
    # SHOW COMPLETION MESSAGE
    # --------------------------------------------------------

    if total_plots == 0:

        print(
            "No channel plots were added to the PDF."
        )

    else:

        root = tk.Tk()
        root.withdraw()

        messagebox.showinfo(
            "Finished",
            f"PDF report created successfully.\n\n"
            f"Plots: {total_plots}\n\n"
            f"Saved to:\n{pdf_path}"
        )

        root.destroy()


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()