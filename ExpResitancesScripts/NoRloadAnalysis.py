import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from nptdms import TdmsFile  # Ensure you have the nptdms library installed: pip install nptdms

# Define the data folder and file
DataFolder = "S:/TriboMedData/CharacterizationData/TENGData/LaserCutSamples/03-04-2025-ExpResistancePI2525/"
DataDir = DataFolder + 'RawData/'
DataDef = DataFolder + 'RawData/24hTest.tdms'

# Sampling rate in Hz
sampling_rate = 1250  # 1250 samples per second

# Load the TDMS file
print(f"Processing file: {DataDef}")
tdms_file = TdmsFile.read(DataDef)

# Extract data from the TDMS file (assuming a single channel for simplicity)
for group in tdms_file.groups():
    for channel in group.channels():
        data = channel.data
        time = np.arange(len(data)) / sampling_rate  # Generate a time axis in seconds

        # Detect positive and negative peaks
        noise_threshold = 0.3  # Only consider peaks higher than ±0.3 volts
        peaks_max, _ = find_peaks(data, height=noise_threshold)  # Positive peaks
        peaks_min, _ = find_peaks(-data, height=noise_threshold)  # Negative peaks

        # Filter valid cycles: A positive peak followed by a negative peak
        valid_peaks_max = []
        valid_peaks_min = []
        for p_max in peaks_max:
            # Find the closest negative peak after the positive peak
            subsequent_min = [p_min for p_min in peaks_min if p_min > p_max]
            if subsequent_min:
                valid_peaks_max.append(p_max)
                valid_peaks_min.append(subsequent_min[0])

        # Plot the signal with detected peaks
        plt.figure(figsize=(12, 6))
        plt.plot(time, data, label='Signal')
        plt.scatter(time[valid_peaks_max], data[valid_peaks_max], color='red', label='Positive Peaks')
        plt.scatter(time[valid_peaks_min], data[valid_peaks_min], color='blue', label='Negative Peaks')
        plt.axhline(0, color='black', linestyle='--', linewidth=0.8, label='Zero Crossing')
        plt.title("Detected Peaks in 24h Test")
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (V)")
        plt.legend()
        plt.tight_layout()
        plt.show()

        # Calculate variability and extreme values
        positive_peak_values = data[valid_peaks_max]
        negative_peak_values = data[valid_peaks_min]
        max_positive = np.max(positive_peak_values) if len(positive_peak_values) > 0 else None
        min_negative = np.min(negative_peak_values) if len(negative_peak_values) > 0 else None
        positive_variability = np.std(positive_peak_values) if len(positive_peak_values) > 0 else None
        negative_variability = np.std(negative_peak_values) if len(negative_peak_values) > 0 else None

        # Plot variability and extreme values
        plt.figure(figsize=(12, 6))
        plt.bar(['Positive Peaks', 'Negative Peaks'], [positive_variability, negative_variability], color=['red', 'blue'])
        plt.title("Variability of Peaks")
        plt.ylabel("Standard Deviation (V)")
        plt.tight_layout()
        plt.show()

        print(f"Maximum Positive Peak: {max_positive:.2f} V")
        print(f"Minimum Negative Peak: {min_negative:.2f} V")
        print(f"Positive Peak Variability (Std Dev): {positive_variability:.2f} V")
        print(f"Negative Peak Variability (Std Dev): {negative_variability:.2f} V")
