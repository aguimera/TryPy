#Importar librerias
import numpy as np  #importa la libreria numpy con el nombre np. Analisis matricial y matematica, tipo matlab
import pandas as pd  #importa la libreria pandas con el nombre pd. Manejo de tablas de datos, tipo excel.
import os
import matplotlib.pyplot as plt  #importa la libreria de graficas
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages  #importar libreria para hacer pdfs

#Arcgivos que seran Exportable. Importo las librerias que anton ha creado para el proyecto.
from TryPy.Calculations import ExtractCyclesByPos, FindTransitionTime
from TryPy.LoadData import Loadfiles
from TryPy.PlotData import GenFigure

# Analisis Estadistico con pandas. boxplots etc.
import seaborn as sns

mpl.use("QtAgg")  #backend es la herramienta de visor de graficas
plt.close('all')  #cerrar todas las graficas antes de empezar
plt.ion()  #activar las graficas que se vean y que no se escondan

#definimos entradas y salidas
DataDir = './Data/'
LoadsDef = './Data/LoadsDescription.ods'

ExpDef = './Data/ExperimentsT1T2CurvesR.xlsx'


# Output Files definition rename if needed
PDF = PdfPages('./Reports/LoadReport-{}.pdf'.format(ExpDef.split('/')[-1].split('.')[0]))
OutFile = './DataSets/Cycles-{}.pkl'.format(ExpDef.split('/')[-1].split('.')[0])

# %% Load Experiments file
dfExp = pd.read_excel(ExpDef)

# If needed implement some selection here
dfExps = dfExp

# %% Load Loads file
dfLoads = pd.read_excel(LoadsDef)
# TODO implement it in the LoadsFile
dfLoads.Req = dfLoads.Req * 1000  # Convert to ohms

# %% Add Loads Fields. Mezcla dos excels en uno con datos de lo dos escogidos
# TODO: update for capacitors
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

# %% Change path to absolute and check if they exist

for index, r in dfExps.iterrows():
    daqFile = os.path.join(DataDir, r.DaqFile)
    if os.path.isfile(daqFile):
        dfExps.loc[index, 'DaqFile'] = daqFile
    else:
        print(f'File {daqFile} not found')
        dfExps.drop(index, inplace=True)
        print("Experiment {} Deleted".format(r.ExpId))

    motorFile = os.path.join(DataDir, r.MotorFile)
    if os.path.isfile(motorFile):
        dfExps.loc[index, 'MotorFile'] = motorFile
    else:
        print(f'File {motorFile} not found')
        dfExps.drop(index, inplace=True)
        print("Experiment {} Deleted".format(r.ExpId))

# %% load data files

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

    # Add more calculations here Example
    for index, r in dfCycle.iterrows():
        cyData = r.Data
        imax = cyData.Current.idxmax()
        imin = cyData.Current.idxmin()
        dfCycle.loc[index, 'CurrentMax'] = cyData.Current[imax]
        dfCycle.loc[index, 'CurrentMin'] = cyData.Current[imin]
        dfCycle.loc[index, 'CurrentMaxPosition'] = cyData.Position[imax]
        dfCycle.loc[index, 'CurrentMinPosition'] = cyData.Position[imin]


    # Stack Cycles for all experiments
    dfCycles = pd.concat([dfCycles, dfCycle])

    # Generate Debug Figures
    XVar = 'Time'
    AxsDict, VarColors = GenFigure(dfData, xVar=XVar, axisFactor=0.1, figsize=(12, 5))
    for var, ax in AxsDict.items():
        if 'Factor' in VarColors[var]:
            ptdata = dfData[var] * VarColors[var]['Factor']
        else:
            ptdata = dfData[var]
        ax.plot(dfData[XVar], ptdata, **VarColors[var]['LineKwarg'])

    for index, r in dfCycle.iterrows():
        ax.axvline(x=r.tStart, color='y', linewidth=2)
        ax.axvline(x=r.tEnd, color='y', linestyle='-.', linewidth=2)
        ax.axvline(x=r.tStart + r.tTransition, color='y', linestyle='--', linewidth=1)
    fig = ax.get_figure()
    fig.suptitle(r.ExpId)
    fig.tight_layout()
    PDF.savefig(fig, bbox_inches='tight')

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
    fig.suptitle(r.ExpId)
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
