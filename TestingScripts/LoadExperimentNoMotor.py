import numpy as np  #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt  #importa la libreria de graficas
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages  #importar libreria para hacer pdfs
from scipy.signal import find_peaks
from operator import concat
from nptdms import TdmsFile
import seaborn as sns
import tkinter as tk
from tkinter import filedialog

mpl.use("Qt5Agg")  #backend es la herramienta de visor de graficas
plt.close('all')  #cerrar todas las graficas antes de empezar
plt.ion()  #activar las graficas que se vean y que no se escondan

DQAColumnRenames = {
    'Input 0': 'Voltage',
    'Unnamed: 1': 'Time',
    'Original Data': 'Voltage DC',
    'AC Signal': 'Voltage with Trend',
    'AC with Trend': 'Voltage',
}


# %% Definition of folders path and files names to use
print("Please provide a file location")
root = tk.Tk()
root.withdraw()  # Amaga la finestra princial de tkinter
root.lift()  # Posa la finestra emergent en primer pla
root.attributes('-topmost', True)  # La finestra sempre al davant
# Carpeta con la lista de archivos CSV y Excel a combinar
DaqFile = filedialog.askopenfilename(title="Select Raw Data File")
if DaqFile:

    # %% Enter  raw data file
    if DaqFile.endswith('.tdms'):
        DaqFile = DaqFile.replace("/", "\\")
        tdms_file = TdmsFile.read(DaqFile)
        dfDAQ = tdms_file.as_dataframe(time_index=True,
                                   scaled_data=False) #create data frame of the file imported
        dfDAQ.reset_index(inplace=True)

        # Optionally rename columns
        dfDAQ = dfDAQ.set_axis(['Time', 'Voltage'], axis=1)
        if 'DQAColumnRenames' in globals():
            dfDAQ = dfDAQ.rename(columns=DQAColumnRenames)

        # %% DATA processing

        # Extract signal and time variables
        signal = dfDAQ['Voltage'].values
        time = dfDAQ['Time'].values

        # Detect local maxima (positive peaks)
        all_pos_peaks, _ = find_peaks(signal,distance=35)
        # Keep only those larger than a manual positive limit
        positive_peaks = all_pos_peaks[signal[all_pos_peaks] > 0.026]
        #Calculate statistics
        mediaPos = signal[positive_peaks].mean()

        #Detect local minima (negative peaks)
        all_neg_peaks, _ = find_peaks(-signal,distance=80)
        # Keep only those lower than a manual negative limit
        negative_peaks = all_neg_peaks[signal[all_neg_peaks] < -0.0772]
        # Calculate statistics
        mediaNeg = signal[negative_peaks].mean()

        #Add results to DataFrame
        dfDAQ['PositivePeak'] = False
        dfDAQ.loc[positive_peaks, 'PositivePeak'] = True
        dfDAQ['NegativePeak'] = False
        dfDAQ.loc[negative_peaks, 'NegativePeak'] = True

    # %% DATA plotting
    #Raw Data Plot
    plt.figure(figsize=(12, 6))
    plt.plot(time, signal, label='Voltage')
    plt.title('Raw Signal')
    plt.xlabel('Time(s)')
    plt.ylabel('Voltage(V)')
    plt.legend()
    plt.grid(True)
    plt.show()

    #Peaks detection plot
    plt.figure(figsize=(12, 6))
    plt.plot(time, signal, label='Voltage')
    plt.plot(time[positive_peaks], signal[positive_peaks], 'go', label='Positive Peaks')
    plt.plot(time[negative_peaks], signal[negative_peaks], 'ro', label='Negative Peaks')
    plt.title('Positive and Negative Peaks in Voltage Signal')
    plt.xlabel('Time(s)')
    plt.ylabel('Voltage(V)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # BoxPlots Statistics
    data=[signal[positive_peaks],signal[negative_peaks]]
    labels = ['Positive Peaks', 'Negative Peaks']
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=data)
    plt.xticks([0, 1], labels)
    plt.title('Peaks Variability', fontsize=14)
    plt.ylabel('Voltage [V]', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()




else:
    print("File Selection Canceled")