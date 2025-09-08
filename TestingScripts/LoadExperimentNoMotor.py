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
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from scipy import signal

mpl.use("Qt5Agg")  #backend es la herramienta de visor de graficas
plt.close('all')  #cerrar todas las graficas antes de empezar
plt.ion()  #activar las graficas que se vean y que no se escondan

DAQColumnRenames = {
    'Input 0': 'Voltage',
    'Amplitude - Plot 0':'Voltage',
    'Time - Plot 0':'Time',
    # # 'Original Data': 'Voltage DC',
    # # 'AC Signal': 'Voltage with Trend',
    # # 'AC with Trend': 'Voltage',
    # 'Voltage': 'Voltage',
    # 'Current': 'Current'
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
        dfDAQ = dfDAQ.set_axis(['Time', 'Voltage'], axis=1)


    elif DaqFile.endswith('.csv'):
        dfDAQ = pd.read_csv(DaqFile,
                            header=0,
                            index_col=False,
                            delimiter=',.',
                            decimal=',')
        # drop Non-defined columns
        dropcols = []
        for col in dfDAQ.columns:
            if col not in DAQColumnRenames.keys():
                dropcols.append(col)
        dfDAQ = dfDAQ.drop(columns=dropcols)
        # rename columns
        dfDAQ = dfDAQ.rename(columns=DAQColumnRenames)

    elif DaqFile.endswith('.xlsx'):
        daqf = pd.ExcelFile(DaqFile)
        sheets = daqf.sheet_names

        # Check if there's more than one sheet
        if len(sheets) > 1:
            sheet_to_use = sheets[1]
        else:
            print(f"⚠️ Only one sheet found in '{DaqFile}'. Using the first one.")
            sheet_to_use = sheets[0]

        dfDAQ = pd.read_excel(DaqFile, sheet_name=sheet_to_use)
        dfDAQ = dfDAQ.rename(columns=DAQColumnRenames)

    # %% Enter  Resistance info
    resistance=1000000 #1 MoHm

    # %% DATA processing

    # Extract signal and time variables
    Signal = dfDAQ['Voltage'].values
    if 'Current' in dfDAQ:
        signalI= dfDAQ['Current'].values
        signalCurrent=signalI/499000
    else:
        print('No current loaded')
    time = dfDAQ['Time'].values

    # Detect local maxima (positive peaks)
    all_pos_peaks, _ = find_peaks(Signal,distance=35)
    # Keep only those larger than a manual positive limit
    positive_peaks = all_pos_peaks[Signal[all_pos_peaks] > 0.25]
    #Calculate statistics
    mediaPos = Signal[positive_peaks].mean()

    #Detect local minima (negative peaks)
    all_neg_peaks, _ = find_peaks(-Signal,distance=80)
    # Keep only those lower than a manual negative limit
    negative_peaks = all_neg_peaks[Signal[all_neg_peaks] < -0.0772]
    # Calculate statistics
    mediaNeg = Signal[negative_peaks].mean()

    #Power Calculations
    Power = dfDAQ.Voltage**2 / resistance
    #E = np.sum(Power) * dt

    #FFT and FILTERING
    nSampsDAQ = Signal.size
    dt = dfDAQ.Time.diff().mean()  # dt entre dos muestras de tiempo, tiempo entre muestras
    DaqFs = 1 / dt  # in Hz
    N=len(Signal)
    freqs = np.fft.rfftfreq(N, 1 / DaqFs) #creates the frequency bins
    cutoff = 30.0  # cutoff frequency (Hz)
    order = 4
    b, a = butter(order, cutoff / (0.5 * DaqFs), btype='low') #low pass filter from 1 Hz
    filtered_signal = filtfilt(b, a, Signal)
    fft_vals = np.fft.rfft(Signal)  # computes the FFT of the signal
    fft_vals_filt = np.fft.rfft(filtered_signal)# computes the FFT of the Filtered signal
    f, Pxx = signal.welch(Signal, DaqFs, nperseg=1024)  # f = frequencies, Pxx = power density PSD

    #Add results to DataFrame
    dfDAQ['PositivePeak'] = False
    dfDAQ.loc[positive_peaks, 'PositivePeak'] = True
    dfDAQ['NegativePeak'] = False
    dfDAQ.loc[negative_peaks, 'NegativePeak'] = True




    # %% DATA plotting
    #Raw Data Plot
    plt.figure(figsize=(12, 6))
    plt.plot(time, Signal, label='Voltage')
    plt.title('Raw Voltage')
    plt.xlabel('Time(s)')
    plt.ylabel('Voltage(V)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # plt.figure(figsize=(12, 6))
    # plt.plot(time, signalCurrent, label='Current')
    # plt.title('Raw Current')
    # plt.xlabel('Time(s)')
    # plt.ylabel('Current(A)')
    # plt.legend()
    # plt.grid(True)
    # plt.show()

    #Peaks detection plot
    plt.figure(figsize=(12, 6))
    plt.plot(time, Signal, label='Voltage')
    plt.plot(time[positive_peaks], Signal[positive_peaks], 'go', label='Positive Peaks')
    plt.plot(time[negative_peaks], Signal[negative_peaks], 'ro', label='Negative Peaks')
    plt.title('Positive and Negative Peaks in Voltage Signal')
    plt.xlabel('Time(s)')
    plt.ylabel('Voltage(V)')
    plt.legend()
    plt.grid(True)
    plt.show()

    # BoxPlots Statistics
    data=[Signal[positive_peaks],Signal[negative_peaks]]
    labels = ['Positive Peaks', 'Negative Peaks']
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=data)
    plt.xticks([0, 1], labels)
    plt.title('Peaks Variability', fontsize=14)
    plt.ylabel('Voltage [V]', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.show()

    # FFT Plot before filter
    plt.figure(figsize=(12, 6))
    plt.subplot(4, 1, 1)
    plt.plot(time, Signal, label="Original")
    plt.title("Time Domain Signal (Before Filtering)")
    plt.legend()
    plt.subplot(4, 1, 2)
    plt.plot(time, filtered_signal, label="Filtered", alpha=0.7)
    plt.title("Time Domain Signal (After Filtering)")
    plt.legend()
    plt.subplot(4, 1, 3)
    plt.plot(freqs, np.abs(fft_vals), label="Original Spectrum")
    plt.title("Frequency Spectrum (Before Filtering)")
    plt.xlim(0, 100)
    plt.subplot(4, 1, 4)
    plt.plot(freqs, np.abs(fft_vals_filt), label="Filtered Spectrum", color='orange')
    plt.title("Frequency Spectrum (After Filtering)")
    plt.xlim(0, 100)
    plt.tight_layout()
    plt.show()

    # Plot
    plt.figure(figsize=(12, 6))
    plt.semilogy(f, Pxx)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('PSD [V²/Hz]')
    plt.title('Power Spectral Density')
    plt.show()

else:
    print("File Selection Canceled")