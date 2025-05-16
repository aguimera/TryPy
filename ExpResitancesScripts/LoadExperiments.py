# From this .py, data will be loaded and a report with raw data graphs will be generated
#Importar librerias
import numpy as np  #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt  #importa la libreria de graficas
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages  #importar libreria para hacer pdfs

#Archivos que seran Exportable. Importo las librerias que anton ha creado para el proyecto.
from TryPy.Calculations import ExtractCyclesByPos, FindTransitionTime
from TryPy.LoadData import Loadfiles
from TryPy.PlotData import GenFigure

# Analisis Estadistico con pandas. boxplots etc.
import seaborn as sns

mpl.use("QtAgg")  #backend es la herramienta de visor de graficas
plt.close('all')  #cerrar todas las graficas antes de empezar
plt.ion()  #activar las graficas que se vean y que no se escondan

# %% Definition of folders path and files names to use

#Inputs definitions
DataFolder = "S:/TriboMedData/CharacterizationData/TENGData/LaserCutSamples/03-04-2025-ExpResistancePI2525/" #Use /, not \
DataDir = DataFolder + 'RawData/'
LoadsDef = DataFolder + 'RawData/LoadsDescription.ods' #Loads excel to use
ExpDef = DataFolder + 'RawData/Experiments.ods' #Excel name to use
TribuId = "'PI2525Au-Sampling'" #TribuID selection from excel name

# Output Definitions
# Creates a PDF in Reports folder with the name LoadReports-ExpDef(previously specified)
PDF = PdfPages(DataFolder + 'Reports/LoadReport-{}.pdf'.format(ExpDef.split('/')[-1].split('.')[0]))
OutFile = DataFolder + 'DataSets/Cycles-{}.pkl'.format(ExpDef.split('/')[-1].split('.')[0])

# %% Read Experiments files
dfExp = pd.read_excel(ExpDef)
dfExps = dfExp.query("TribuId == " + TribuId)

# %% Read Loads fles
dfLoads = pd.read_excel(LoadsDef)
LoadsFields = ('Req', 'Gain')  # List of fields from LoadsDef to add
for lf in LoadsFields:
    if lf not in dfExps.columns:
        dfExps.insert(1, lf, None)
# Check if load exists
for index, r in dfExps.iterrows():
    if r.RloadId in dfLoads.RloadId.values:
        for lf in LoadsFields:
            dfExps.loc[index, lf] = dfLoads.loc[dfLoads.RloadId == r.RloadId, lf].values
    else:
        print(f'Warning Load {r.RloadId} not found !!!!')
        dfExps.drop(index, inplace=True)
        print("Experiment {} Deleted".format(r.ExpId))

# %% Change path to absolute and check if data files exist
for index, r in dfExps.iterrows():
#Check DAQ INFO
    daqFile = os.path.join(DataDir, r.DaqFile)
    if os.path.isfile(daqFile):
        dfExps.loc[index, 'DaqFile'] = daqFile
    else:
        print(f'File {daqFile} not found')
        dfExps.drop(index, inplace=True)
        print("Experiment {} Deleted".format(r.ExpId))
#Check Motor INFO
    motorFile = os.path.join(DataDir, r.MotorFile)
    if os.path.isfile(motorFile):
        dfExps.loc[index, 'MotorFile'] = motorFile
    else:
        print(f'File {motorFile} not found')
        dfExps.drop(index, inplace=True)
        print("Experiment {} Deleted".format(r.ExpId))

# %% DATA PROCESSING
plt.ioff()
dfCycles = pd.DataFrame()
for index, r in dfExps.iterrows():
    print(f'Processing: {r.ExpId}')

    # Load data files
    dfData = Loadfiles(r)

    # Reference position and force
    dfData.Position = dfData.Position - dfData.Position.min()
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

    # Extract analytical information per cycle
    for index, r in dfCycle.iterrows():
        cyData = r.Data
        imax = cyData.Current.idxmax()
        imin = cyData.Current.idxmin()
        dfCycle.loc[index, 'CurrentMax'] = cyData.Current[imax] #Positive peak
        dfCycle.loc[index, 'CurrentMin'] = cyData.Current[imin] #Negative peak
        dfCycle.loc[index, 'CurrentMaxPosition'] = cyData.Position[imax] #Positive peak position
        dfCycle.loc[index, 'CurrentMinPosition'] = cyData.Position[imin] #Negative peak position
        dfCycle.loc[index, 'PosPulseWidth'] = cyData.Current #Positive peak width (s)
        dfCycle.loc[index, 'NegPulseWidth'] = cyData.Current #Negative peak width (s)

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

    for index, r in dfCycle.iterrows():    # Generates yellow separation lines to start, end of the cycles
        ax.axvline(x=r.tStart, color='y', linewidth=1)
        ax.axvline(x=r.tEnd, color='y', linestyle='-.', linewidth=1)
        ax.axvline(x=r.tStart + r.tTransition, color='y', linestyle='--', linewidth=1)

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
    fig = ax.get_figure()
    # fig.suptitle(r.ExpId)
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