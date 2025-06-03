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

mpl.use("Qt5Agg")  #backend es la herramienta de visor de graficas
plt.close('all')  #cerrar todas las graficas antes de empezar
plt.ion()  #activar las graficas que se vean y que no se escondan

# %% Definition of folders path and files names to use

#Inputs definitions
DataFolder = "C:/Users/mmartic/OneDrive - INSTITUT CATALA DE NANOCIENCIA I NANOTECNOLOGIA/Documents/EXPelectrodes/" #Use /, not \
DataDir = DataFolder + 'RawData/'
LoadsDef = DataFolder + 'RawData/LoadsDescription.ods' #Loads excel to use
ExpDef = DataFolder + 'RawData/ExperimentsNewElectrodes.xlsx' #Excel name to use
TribuId = "'RC-TENG'" #TribuID selection from excel name

# Output Definitions
# Creates a PDF in Reports folder with the name LoadReports-ExpDef(previously specified)
PDF = PdfPages(DataFolder + 'Reports/LoadReport-{}.pdf'.format(ExpDef.split('/')[-1].split('.')[0]))
OutFile = DataFolder + 'DataSets/Cycles-{}.pkl'.format(ExpDef.split('/')[-1].split('.')[0])

# %% Read Experiments Excel
dfExp = pd.read_excel(ExpDef)
dfExps = dfExp.query("TribuId == " + TribuId)

# %% Read Loads excel
dfLoads = pd.read_excel(LoadsDef)
#Check if Req and Gain column exists
LoadsFields = ('Req', 'Gain','Ceq')  # List of fields from LoadsDef to add
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
                dfExps.loc[index, lf] = 1000 # Assign a very low resistance just for trying in Ohms
            elif lf == 'Gain':
                dfExps.loc[index, lf] = 1
            elif lf== 'Ceq':
                dfExps.loc[index, lf] = float('inf')
    else:
        print(f'Warning Load {r.RloadId} not found !!!! (Assigned ∞)')
        for lf in LoadsFields:
            dfExps.loc[index, lf] = float('inf')  # Assign open-circuit behavior

        # dfExps.drop(index, inplace=True)
        # print("Experiment {} Deleted".format(r.ExpId))

# %% Change path to absolute and check if data files exist
for index, r in dfExps.iterrows():
#Check DAQ path
    daqFile = os.path.join(DataDir, r.DaqFile) #Complete Path of the DAQ file
    if os.path.isfile(daqFile): #If exists, updates DaqFile column with the complete path to the DAQ file
        dfExps.loc[index, 'DaqFile'] = daqFile
    else:
        print(f'File {daqFile} not found')
        dfExps.drop(index, inplace=True)
        print("Experiment {} Deleted".format(r.ExpId))
#Check Motor path
    motorFile = os.path.join(DataDir, r.MotorFile) #Complete Path of the Motor file
    if os.path.isfile(motorFile): #If exists, updates motorFile column with the complete path to the motor file
        dfExps.loc[index, 'MotorFile'] = motorFile
    else:
        print(f'File {motorFile} not found')
        dfExps.drop(index, inplace=True)
        print("Experiment {} Deleted".format(r.ExpId))

# %% DATA PROCESSING
plt.ioff()
dfCycles = pd.DataFrame() #Inicialización
for index, r in dfExps.iterrows(): #Para cada fila del último dfExps
    print(f'Processing: {r.ExpId}')
    # Creates DataFrame with DAQ(V,I,P) and Motor(Position, Force, etc) Data
    dfData = Loadfiles(r)
    # Reference position and force
    dfData.Position = dfData.Position - dfData.Position.min() #Offset so position starts at 0
    dfData.Force = -dfData.Force
    # Extract Cycles
    CyclesList = ExtractCyclesByPos(dfData,
                                    ContactPosition=r.ContactPosition,
                                    Latency=r.Latency,
                                    )

    # Convert Cycles to DataFrame with experiment information
    for cy in CyclesList:
        cy.update(r.to_dict())
    dfCycle = pd.DataFrame(CyclesList)

    # Find Transition Time
    dfCycle = FindTransitionTime(dfCycle)

    # Extract analytical information PER CYCLE
    for index, r in dfCycle.iterrows():
        cyData=r.Data
        imax = cyData.Current.idxmax()#Local Cycle  of the Max Current Peak found for the cycle
        imin = cyData.Current.idxmin()#Local Cycle  of the Min Current Peak found for the cycle
        MaxPeakWidth=peak_widths(cyData.Current,[imax],rel_height=0.5) #Positive peaks widths
        MinPeakWidth=peak_widths(-cyData.Current,[imin],rel_height=0.5) #Negative peaks widths
        MaxPeakWidth=MaxPeakWidth[0]*cyData.Time.diff().mean() #pass from samples to seconds
        MinPeakWidth = MinPeakWidth[0] * cyData.Time.diff().mean()  # pass from samples to seconds
        dfCycle.loc[index, 'CurrentMax'] = cyData.Current[imax] #Positive peak
        dfCycle.loc[index, 'CurrentMin'] = cyData.Current[imin] #Negative peak
        dfCycle.loc[index, 'CurrentMaxPosition'] = cyData.Position[imax] #Positive peak position
        dfCycle.loc[index, 'CurrentMaxTime'] = cyData.Time[imax]  # Positive peak position
        dfCycle.loc[index, 'CurrentMinTime'] = cyData.Time[imin]  # Positive peak position
        dfCycle.loc[index, 'CurrentMinPosition'] = cyData.Position[imin] #Negative peak position
        dfCycle.loc[index, 'PositivePulseWidth'] = MaxPeakWidth #Positive peak width (s)
        dfCycle.loc[index, 'NegativePulseWidth'] = MinPeakWidth #Negative peak width (s)
    # Stack Cycles for all experiments
    dfCycles = pd.concat([dfCycles, dfCycle])

# %% DATA PLOTTING

    #Plot Signal vs Time
    XVar = 'Time'
    AxsDict, VarColors = GenFigure(dfData, xVar=XVar, axisFactor=0.1, figsize=(12, 5))
    for var, ax in AxsDict.items():
        if 'Factor' in VarColors[var]:
            ptdata = dfData[var] * VarColors[var]['Factor']
        else:
            ptdata = dfData[var]
        ax.plot(dfData[XVar], ptdata, **VarColors[var]['LineKwarg']) # Plotea cada columna

    #for index, r in dfCycle.iterrows():    # Generates yellow separation lines to start, end of the cycles
    #    ax.axvline(x=r.tStart, color='y', linewidth=0.5)
    #    ax.axvline(x=r.tEnd, color='y', linestyle='-.', linewidth=0.5)
    #    ax.axvline(x=r.tStart + r.tTransition, color='y', linestyle='--', linewidth=0.5)

    fig = ax.get_figure()
    fig.suptitle(r.ExpId)
    fig.suptitle(f'Req: {r.Req / 1e6:.2f} MΩ, {r.ExpId}')
    fig.tight_layout()
    PDF.savefig(fig, bbox_inches='tight')

    # Plot Signal vs Position
    XVar = 'Position'
    AxsDict, VarColors = GenFigure(dfData, xVar=XVar, figsize=(12, 5))
    for var, ax in AxsDict.items():
        if 'Factor' in VarColors[var]:
            ptdata = dfData[var] * VarColors[var]['Factor']
        else:
            ptdata = dfData[var]
        ax.plot(dfData[XVar], ptdata, **VarColors[var]['LineKwarg'])

    ax.set_xlim(0, 3)
    ax.set_xlabel('Position [mm]')
    fig = ax.get_figure()
    fig.suptitle(r.ExpId)
    fig.suptitle(f'Req: {r.Req / 1e6:.2f} MΩ')
    fig.tight_layout()
    PDF.savefig(fig, bbox_inches='tight')
    plt.close('all')



plt.ion()
PDF.close()

dfCycles.reset_index(inplace=True, drop=True)
dfCycles = dfCycles.astype({'Gain': float,
                            'Req': float,
                            })

dfCycles.to_pickle(OutFile)