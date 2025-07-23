# From this .py, data will be loaded and a report with raw data graphs will be generated
#Importar librerias
import numpy as np  #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt  #importa la libreria de graficas
import matplotlib as mpl
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

mpl.use("Qt5Agg")  #backend es la herramienta de visor de graficas
plt.close('all')  #cerrar todas las graficas antes de empezar
plt.ion()  #activar las graficas que se vean y que no se escondan

# %% Definition of folders path and files names to use
print("Please provide a folder location")
root = tk.Tk()
root.withdraw()  # Amaga la finestra princial de tkinter
root.lift()  # Posa la finestra emergent en primer pla
root.attributes('-topmost', True)  # La finestra sempre al davant
# Carpeta con la lista de archivos CSV y Excel a combinar
DataFolder = filedialog.askdirectory(title="Select Experiment Folder directory")
if DataFolder:
    DataFolder = DataFolder.replace("/", "\\")

print("Please provide a file location")
root = tk.Tk()
root.withdraw()  # Amaga la finestra princial de tkinter
root.lift()  # Posa la finestra emergent en primer pla
root.attributes('-topmost', True)  # La finestra sempre al davant
# Carpeta con la lista de archivos CSV y Excel a combinar
RawDAQ = filedialog.askopenfilename(title="Select Teng DAQ file")
if RawDAQ:
    RawDAQ = RawDAQ.replace("/", "\\")

print("Please provide a file location")
root = tk.Tk()
root.withdraw()  # Amaga la finestra princial de tkinter
root.lift()  # Posa la finestra emergent en primer pla
root.attributes('-topmost', True)  # La finestra sempre al davant
# Carpeta con la lista de archivos CSV y Excel a combinar
RawMotor = filedialog.askopenfilename(title="Select Motor file")
if RawMotor:
    RawMotor = RawMotor.replace("/", "\\")



RawMotor = pd.read_excel(RawMotor) #