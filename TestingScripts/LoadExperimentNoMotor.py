import numpy as np  #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt  #importa la libreria de graficas
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages  #importar libreria para hacer pdfs
from scipy.signal import find_peaks
from operator import concat
from nptdms import TdmsFile
#Archivos que seran Exportable. Importo las librerias que anton ha creado para el proyecto.
from TryPy.LoadData import Loadfiles
from TryPy.LoadData import LoadDAQFile
from TryPy.PlotData import GenFigure
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
    if DaqFile.endswith('.tdms'):
        DaqFile = DaqFile.replace("/", "\\")
        tdms_file = TdmsFile.read(DaqFile)
        dfDAQ = tdms_file.as_dataframe(time_index=True,
                                   scaled_data=False)
        dfDAQ.reset_index(inplace=True)
        # dfDAQ = dfDAQ.iloc[:, :2]
        dfDAQ = dfDAQ.set_axis(['Time', 'Voltage'], axis=1)
        # Optionally rename columns if DQAColumnRenames is defined
    if 'DQAColumnRenames' in globals():
        dfDAQ = dfDAQ.rename(columns=DQAColumnRenames)

        signal = dfDAQ['Voltage'].values
        time = dfDAQ['Time'].values

        # --- Detect local maxima (positive peaks) ---
        all_pos_peaks, _ = find_peaks(signal,distance=35)
        # Keep only those with strictly positive values
        positive_peaks = all_pos_peaks[signal[all_pos_peaks] > 0.026]
        mediaPos = signal[positive_peaks].mean()

        # --- Detect local minima (negative peaks) ---
        all_neg_peaks, _ = find_peaks(-signal,distance=80)
        # Keep only those with strictly negative values
        negative_peaks = all_neg_peaks[signal[all_neg_peaks] < -0.0772]
        mediaNeg = signal[negative_peaks].mean()
        # --- Add results to DataFrame ---
        dfDAQ['PositivePeak'] = False
        dfDAQ.loc[positive_peaks, 'PositivePeak'] = True
        dfDAQ['NegativePeak'] = False
        dfDAQ.loc[negative_peaks, 'NegativePeak'] = True

     # --- Plot the results ---
    plt.figure(figsize=(12, 6))
    plt.plot(time, signal, label='Voltage')
    plt.xlabel('Time')
    plt.ylabel('Voltage')
    plt.legend()
    plt.grid(True)
    plt.show()

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

    labels = ['Picos Positivos', 'Picos Negativos']
    values = [mediaPos, mediaNeg]
    colors = ['skyblue', 'salmon']
    plt.figure(figsize=(12, 6))
    bars=plt.bar(labels, values, color=colors)
    # Agregar valores encima de cada barra
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.2 * (1 if yval >= 0 else -1),
                 f'{yval:.2f}', ha='center', va='bottom' if yval >= 0 else 'top')
    # Títulos y etiquetas
    plt.title('Positive and negative peaks mean', fontsize=14)
    plt.ylabel('Voltaje [V]', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

else:
    print("File Selection Canceled")