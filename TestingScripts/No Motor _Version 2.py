# From this .py, data will be loaded and a report with raw data graphs will be generated
# Importar librerias
import numpy as np  # importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  # importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import sys
import matplotlib.pyplot as plt  # importa la libreria de graficas
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages  # importar libreria para hacer pdfs
from scipy.signal import peak_widths
from operator import concat
from scipy.integrate import simpson

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

# Archivos que seran Exportable. Importo las librerias que anton ha creado para el proyecto.
from TryPy.Calculations import ExtractCyclesByPos, FindTransitionTime
from TryPy.LoadData import LoadDAQFile
from TryPy.PlotData import GenFigure
import seaborn as sns
import tkinter as tk
from tkinter import filedialog

mpl.use("Qt5Agg")  # backend es la herramienta de visor de graficas
plt.close('all')  # cerrar todas las graficas antes de empezar
plt.ion()  # activar las graficas que se vean y que no se escondan

def calculate_energy(power_series, time_series):
    """
    Calculate energy by integrating power over time using trapezoidal method
    power_series: array of power values in watts
    time_series: array of time values in seconds
    returns: energy in joules
    """
    # Ensure both arrays have the same length by removing last few samples
    min_length = min(len(power_series), len(time_series))  # Remove extra 5 samples for safety
    power_series = power_series[:min_length]
    time_series = time_series[:min_length]
    
    # Calculate time differences between consecutive samples
    dt = np.diff(time_series)
    # Calculate average power between consecutive samples
    avg_power = (power_series[:-1] + power_series[1:]) / 2
    # Multiply and sum to get total energy
    return np.sum(avg_power * dt)

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
LoadsDef = filedialog.askopenfilename(title="Select Loads Description file")
if LoadsDef:
    LoadsDef = LoadsDef.replace("/", "\\")

print("Please provide a file location")
root = tk.Tk()
root.withdraw()  # Amaga la finestra princial de tkinter
root.lift()  # Posa la finestra emergent en primer pla
root.attributes('-topmost', True)  # La finestra sempre al davant
# Carpeta con la lista de archivos CSV y Excel a combinar
ExpDef = filedialog.askopenfilename(title="Select Experiments Description excel file")
if ExpDef:
    ExpDef = ExpDef.replace("/", "\\")
if LoadsDef and ExpDef and DataFolder:

    ### Inputs definitions
    DataDir = DataFolder + '\\RawData\\'
    TribuId = "'PI5878G-Nylon6'"  # TribuID selection from excel name

    # Output Definitions
    # Creates a PDF in Reports folder with the name LoadReports-ExpDef(previously specified)
    PDF = PdfPages(DataFolder + '\\Reports\\LoadReport-{}.pdf'.format(ExpDef.split('\\')[-1].split('.')[0]))
    OutFile = DataFolder + '\\DataSets\\Cycles-{}.pkl'.format(ExpDef.split('\\')[-1].split('.')[0])

    # %% Read Experiments Excel
    dfExp = pd.read_excel(ExpDef)
    dfExps = dfExp.query("TribuId == " + TribuId)

    # %% Read Loads excel
    dfLoads = pd.read_excel(LoadsDef)
    # Check if Req and Gain column exists
    LoadsFields = ('Req', 'Gain', 'Ceq')  # List of fields from LoadsDef to add
    for lf in LoadsFields:
        if lf not in dfExps.columns:
            dfExps.insert(1, lf, None)
    # Check RLoad conditions
    for index, r in dfExps.iterrows():  # For each row
        if r.RloadId in dfLoads.RloadId.values:
            for lf in LoadsFields:
                dfExps.loc[index, lf] = dfLoads.loc[dfLoads.RloadId == r.RloadId, lf].values[0]
        elif r.RloadId == 'ElectrodeImpedance':
            print(f'Warning Load {r.RloadId} is Electrode Impedance, Assigned 80 kOhms')
            for lf in LoadsFields:
                if lf == 'Req':
                    dfExps.loc[index, lf] = 1000  # Assign a very low resistance just for trying in Ohms
                elif lf == 'Gain':
                    dfExps.loc[index, lf] = 1
        else:
            print(f'Warning Load {r.RloadId} not found !!!! (Assigned ∞)')
            for lf in LoadsFields:
                dfExps.loc[index, lf] = float('inf')  # Assign open-circuit behavior


    # %% Change path to absolute and check if data files exist
    for index, r in dfExps.iterrows():
        # Check DAQ path
        daqFile = os.path.join(DataDir, r.DaqFile)  # Complete Path of the DAQ file
        if os.path.isfile(daqFile):  # If exists, updates DaqFile column with the complete path to the DAQ file
            dfExps.loc[index, 'DaqFile'] = daqFile
        else:
            print(f'File {daqFile} not found')
            dfExps.drop(index, inplace=True)
            print("Experiment {} Deleted".format(r.ExpId))
    # %% DATA PROCESSING
    dfDAQ=pd.DataFrame()
    dfData=pd.DataFrame()
    dfPower=pd.DataFrame()
    dfEnergy=pd.DataFrame()
    
    # Lists to store resistance and energy values for plotting
    resistances = []
    energies = []
    
    for index, r in dfExps.iterrows():  # Para cada fila del último dfExps
        print(f'Processing: {r.ExpId}')
        col_name = f"Voltage_{r.Req}"
        col_name_P = f"Power_{r.Req}"
        col_name_E = f"Energy_{r.Req}"
        # Read DAQ fILE
        dfDAQ=LoadDAQFile(r.DaqFile)
        dfData['Time'] = dfDAQ.Time  # Extracts Time Column
        dfData[col_name] = dfDAQ.Voltage # Extracts all voltage column for each R
        dfPower[col_name_P] = dfData[col_name]**2 / r.Req #Calculates Power per each Voltage

        # Calculate energy using our custom function
        dfEnergy.loc[0, col_name_E] = calculate_energy(
            dfPower[col_name_P].values,
            dfDAQ.Time.values
        )
        
        # Store values for plotting
        resistances.append(r.Req)
        energies.append(dfEnergy.loc[0, col_name_E])

        # DAQ sampling rate
        if 'Time' in dfDAQ.columns:
            nSampsDAQ = dfDAQ.Voltage.size
            dt = dfDAQ.Time.diff().mean()  # dt entre dos muestras de tiempo, tiempo entre muestras
            DaqFs = 1 / dt  # in Hz
            print(f'Found DAQ sampling rate: {DaqFs}')

    # Create energy vs resistance plot
    plt.figure(figsize=(10, 6))
    plt.plot(resistances, energies, 'bo-', linewidth=2, markersize=8)
    plt.xscale('log')  # Log scale for resistance
    plt.grid(True)
    plt.xlabel('Resistance (Ω)')
    plt.ylabel('Energy (J)')
    plt.title('Energy vs Load Resistance')
    
    # Generate timestamp and save plot with timestamp in Reports folder
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
    plot_filename = os.path.join(DataFolder, 'Reports', f'energy_vs_resistance_{timestamp}.png')
    plt.savefig(plot_filename)
    plt.close()

     # %% DATA plotting
     #    # Voltage PLOTS
     #    for col in dfData.columns[1:]:
     #        plt.figure(figsize=(12, 6))
     #        plt.plot(dfData.Time, dfData[col], label='Voltage')
     #        plt.title(f"Voltage_{r.Req}")
     #        plt.xlabel('Time(s)')
     #        plt.ylabel('Voltage(V)')
     #        plt.legend()
     #        plt.grid(True)
     #        plt.show()
     #
     #    # Power PLOTS
     #    for col in dfPower.columns:
     #        plt.figure(figsize=(12, 6))
     #        plt.plot(dfData.Time, dfPower[col], label='Power')
     #        plt.title(f"Power_{r.Req}")
     #        plt.xlabel('Time(s)')
     #        plt.ylabel('Power(W)')
     #        plt.legend()
     #        plt.grid(True)
     #        plt.show()
     #
     #    for col in dfEnergy.columns:
     #        plt.figure(figsize=(12, 6))
     #        plt.plot(r.Req, dfEnergy[col], label='Power')
     #        plt.title(f"Power_{r.Req}")
     #        plt.xlabel('Time(s)')
     #        plt.ylabel('Power(W)')
     #        plt.legend()
     #        plt.grid(True)
     #        plt.show()
else:
    print("File Selection Canceled")