import os
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from nptdms import TdmsFile  # Ensure you have the nptdms library installed: pip install nptdms

def calculate_power_vs_resistance(DataFolder, noise_threshold=0.2):
    """
    Calculates power vs resistance (P vs R) for each .tdms file in the RawData folder.

    Args:
        DataFolder (str): Root folder containing the RawData directory.
        noise_threshold (float): Minimum absolute value for peaks to be considered valid.

    Returns:
        None
    """
    # Define input and output paths
    DataDir = os.path.join(DataFolder, 'RawData')
    ReportsDir = os.path.join(DataFolder, 'Reports')
    os.makedirs(ReportsDir, exist_ok=True)  # Ensure the Reports directory exists

    # Create a PDF to save plots
    pdf_path = os.path.join(ReportsDir, 'Power_vs_Resistance_Report.pdf')
    PDF = PdfPages(pdf_path)

    # Initialize a DataFrame to store results
    results = []

    try:
        # Iterate through all .tdms files in the RawData folder
        for file_name in os.listdir(DataDir):
            if file_name.endswith('.tdms'):
                file_path = os.path.join(DataDir, file_name)
                print(f"Processing file: {file_path}")

                # Load the TDMS file
                tdms_file = TdmsFile.read(file_path)

                # Extract data from the TDMS file (assuming a single channel for simplicity)
                for group in tdms_file.groups():
                    for channel in group.channels():
                        data = channel.data
                        time = np.arange(len(data))  # Generate a time axis

                        # Detect peaks (maxima and minima)
                        peaks_max, _ = find_peaks(data)
                        peaks_min, _ = find_peaks(-data)

                        # Filter out noise near 0 volts
                        peaks_max = [p for p in peaks_max if data[p] > noise_threshold]
                        peaks_min = [p for p in peaks_min if data[p] < -noise_threshold]

                        # Plot detected peaks
                        plt.figure(figsize=(10, 6))
                        plt.plot(time, data, label='Signal')
                        plt.scatter(time[peaks_max], data[peaks_max], color='red', label='Max Peaks')
                        plt.scatter(time[peaks_min], data[peaks_min], color='blue', label='Min Peaks')
                        plt.title(f"Detected Peaks for {file_name}")
                        plt.xlabel("Time")
                        plt.ylabel("Signal Value")
                        plt.legend()
                        plt.tight_layout()
                        PDF.savefig()  # Save the plot to the PDF
                        plt.close()

                        # Calculate peak-to-peak voltage
                        if len(peaks_max) > 0 and len(peaks_min) > 0:
                            V_max = data[peaks_max].max()
                            V_min = data[peaks_min].min()
                            V_pp = V_max - V_min  # Peak-to-peak voltage

                            # Extract resistance value from the file name (e.g., "0304DAQ01.tdms")
                            resistance = extract_resistance_from_filename(file_name)

                            # Calculate power: P = V^2 / R
                            if resistance > 0:
                                power = (V_pp ** 2) / resistance
                                results.append({'Resistance': resistance, 'Power': power})

        # Plot Power vs Resistance
        if results:
            results_df = pd.DataFrame(results)
            plt.figure(figsize=(10, 6))
            plt.scatter(results_df['Resistance'], results_df['Power'], color='green', label='Power vs Resistance')
            plt.title("Power vs Resistance")
            plt.xlabel("Resistance (Ω)")
            plt.ylabel("Power (W)")
            plt.legend()
            plt.tight_layout()
            PDF.savefig()  # Save the plot to the PDF
            plt.close()

        # Save results to a CSV file
        results_df = pd.DataFrame(results)
        results_csv_path = os.path.join(ReportsDir, 'Power_vs_Resistance_Results.csv')
        results_df.to_csv(results_csv_path, index=False)
        print(f"Results saved to: {results_csv_path}")
        print(f"PDF report generated: {pdf_path}")
    finally:
        PDF.close()  # Ensure the PDF is closed properly


def extract_resistance_from_filename(file_name):
    """
    Extracts the resistance value from the file name.

    Args:
        file_name (str): Name of the .tdms file.

    Returns:
        float: Resistance value in ohms.
    """
    # Example: Extract resistance from file name (e.g., "0304DAQ01.tdms")
    # You can modify this logic based on your file naming convention
    resistance_mapping = {
        "0304DAQ01.tdms": 1000000,  # Resistance in ohms
        "0304DAQ02.tdms": 5000000,
        "0304DAQ03.tdms": 10000000,
        "0304DAQ04.tdms": 20000000,
        "0304DAQ05.tdms": 30000000,
        "0304DAQ06.tdms": 40000000,
        "0304DAQ07.tdms": 50000000,
        "0304DAQ08.tdms": 60000000,
        "0304DAQ09.tdms": 70000000,
        "0304DAQ10.tdms": 80000000,
        "0304DAQ11.tdms": 90000000,
        "0304DAQ12.tdms": 100000000,
    }
    return resistance_mapping.get(file_name, 0)  # Default to 0 if not found


# Call the function with the data folder
DataFolder = "S:/TriboMedData/CharacterizationData/TENGData/LaserCutSamples/03-04-2025-ExpResistancePI2525"
calculate_power_vs_resistance(DataFolder, noise_threshold=0.1)