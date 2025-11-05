# From this .py, data will be loaded and a report with raw data graphs will be generated
#Importar librerias
import numpy as np  #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt  #importa la libreria de graficas
import matplotlib as mpl
from fontTools.misc.fixedTools import strToFixedToFloat
from matplotlib.backends.backend_pdf import PdfPages  #importar libreria para hacer pdfs
from scipy.signal import peak_widths, medfilt
from operator import concat
from scipy.stats import linregress

#Archivos que seran Exportable. Importo las librerias que anton ha creado para el proyecto.
from TryPy.Calculations import ExtractCyclesByPos, FindTransitionTime
from TryPy.LoadData import Loadfiles
from TryPy.PlotData import GenFigure
import seaborn as sns
import tkinter as tk
from tkinter import filedialog


print("Please provide a file location")
root = tk.Tk()
root.withdraw()  # Amaga la finestra princial de tkinter
root.lift()  # Posa la finestra emergent en primer pla
root.attributes('-topmost', True)  # La finestra sempre al davant
# Carpeta con la lista de archivos CSV y Excel a combinar
DaqFile = filedialog.askopenfilename(title="Select Raw Data File")


dfDAQ = pd.read_csv(DaqFile,
                            header=16,
                            index_col=False,
                            delimiter=',',
                            decimal=',')

DAQColumnRenames = {
    'DMM-1 Time (s)': 'Time(s)',
    'DMM-1 Charge (C)':'Charge(C)',
    'Index': 'Index',
}
# rename columns
dfDAQ = dfDAQ.rename(columns=DAQColumnRenames)

Time=dfDAQ['Time(s)'].values
Time=(Time[:116])
Time_float=np.array([])
for c in Time:
    Time_str=c.replace(',','.')
    Time_float=np.append(Time_float,float(Time_str))

Charge=dfDAQ['Charge(C)'].values
Charge=Charge[:116]
Charge_float=np.array([])
for c in Charge:
    Charge_str=c.replace(',','.')
    Charge_float=np.append(Charge_float,float(Charge_str))


Charge_dif=np.diff(Charge_float, axis=0)
window = 5
Charge_diff_filtered = np.convolve(Charge_dif, np.ones(window)/window, mode='same')
plt.plot(Charge_diff_filtered)
plt.show()

start_idx=0
end_idx=0
max_charge = max(Charge_diff_filtered)
for i in range(Charge_diff_filtered.shape[0]):
    if Charge_diff_filtered[i] > max_charge*0.5:
        if start_idx == 0:
            start_idx = i
        end_idx = i


# --- Step 1: Identify the "middle linear region" automatically ---
# One heuristic approach: take the central 40–60% of data
n = len(Time_float)
#start_idx = int(n * 0.3)
#end_idx = int(n * 0.7)

time_mid = Time_float[start_idx:end_idx]
charge_mid = Charge_float[start_idx:end_idx]

# --- Step 2: Fit a line to that region ---
slope, intercept, r_value, p_value, std_err = linregress(time_mid, charge_mid)

print(f"Slope of the fitted line (middle region): ", slope)

# --- Step 3: Plot the data and fitted line ---
plt.figure(figsize=(8,5))
plt.plot(Time_float, Charge_float, label="Full Data", alpha=0.6)
plt.plot(time_mid, charge_mid, 'o', label="Middle Region", color='orange')
plt.plot(time_mid, intercept + slope*time_mid, 'r--', label=f"Fit: y={slope:.3e}x+{intercept:.3e}")
plt.xlabel("Time")
plt.ylabel("Charge")
plt.legend()
plt.title("Linear Fit to Middle Slope Region")
plt.show()

