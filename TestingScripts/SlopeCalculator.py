# From this .py, data will be loaded and a report with raw data graphs will be generated
#Importar librerias
import numpy as np  #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt  #importa la libreria de graficas
import matplotlib as mpl
from fontTools.misc.fixedTools import strToFixedToFloat
from matplotlib.backends.backend_pdf import PdfPages  #importar libreria para hacer pdfs
from scipy.signal import peak_widths
from operator import concat

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
for d in Charge_float:

Charge_float
matplotlib.

plt.figure(figsize=(12, 6))
plt.plot( Time_float,Charge_float)
plt.title('Charge Integration')
plt.xlabel('Time(s)')
plt.ylabel('Charge(C)')
plt.tight_layout()
plt.show()
