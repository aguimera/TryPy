from math import ceil

import numpy as np
import pandas as pd
import os
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.integrate import simpson

from TryPy.PlotData import PlotScalarValues, GenFigure
# import imageio.v2 as imageio  # Importar la versión 2 de imageio para evitar el aviso de deprecación

PDF = PdfPages('./Reports/DataSetsAnalysis.pdf')

# %% Load data

FileIn = './DataSets/Cycles-ExperimentsT1T2CurvesR.pkl'
dfData = pd.read_pickle(FileIn)


# %% add new calculations example
for index, r in dfData.iterrows():
    cyData = r.Data
    dfData.loc[index, 'VoltageMax'] = cyData.Voltage.max()
    dfData.loc[index, 'VoltageMin'] = cyData.Voltage.min()
    dfData.loc[index, 'Energy'] = simpson(y=cyData.Power, x=cyData.Time)
    IndHalf = int(r.iTransition)
    dfData.loc[index, 'PositiveEnergy'] = simpson(y=cyData.Power[:IndHalf], x=cyData.Time[:IndHalf])
    dfData.loc[index, 'NegativeEnergy'] = simpson(y=cyData.Power[IndHalf:], x=cyData.Time[IndHalf:])






# %% Plot experiments comparison

PlotPars = ('CurrentMax',
            'CurrentMin',
            'CurrentMaxPosition',
            'CurrentMinPosition',)

fig, axs = PlotScalarValues(dfData=dfData,
                            PlotPars=PlotPars,
                            xVar='Req',
                            hueVar='TribuId',
                            PltFunt=sns.scatterplot)


# %% compare positive and negative peaks

dSel = dfData.query("TribuId == 'SwTENG-R' ")
fig, ax = plt.subplots()
sns.lineplot(data=dSel,
             x='Req',
             y='PositiveEnergy',
             ax=ax,
             label='PositiveEnergy')
sns.lineplot(data=dSel,
             x='Req',
             y='NegativeEnergy',
             ax=ax,
             label='NegativeEnergy')
sns.lineplot(data=dSel,
             x='Req',
             y='Energy',
             ax=ax,
             label='Energy')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Load Resistance (Ohm)')
ax.set_ylabel('Energy (J)')
ax.legend()
PDF.savefig(fig)



# Gráfica para Energia en función de T1 Y T2
# Obtener los nombres de los diferentes valores de ExpId
# Configurar el gráfico
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Contact Time Effect')
# Trazar los puntos para PosEnergy, NegEnergy y Energy en función de ExpId
sns.scatterplot(data=dfData, x='ExpId', y='PositiveEnergy', ax=ax, label='PosEnergy', color='blue')
sns.scatterplot(data=dfData, x='ExpId', y='NegativeEnergy', ax=ax, label='NegEnergy', color='red')
sns.scatterplot(data=dfData, x='ExpId', y='Energy', ax=ax, label='Energy', color='green')

ax.set_xlabel('ExpId')
ax.set_ylabel('Energy (J)')
ax.legend()

plt.xticks(rotation=45)  # Rotar las etiquetas del eje x para una mejor legibilidad
plt.tight_layout()
PDF.savefig(fig)



# Crear el directorio "images" si no existe
if not os.path.exists('images'):
    os.makedirs('images')
# %% Plot experiment time traces

VarColors = {
    'Voltage': {'LineKwarg': {'color': 'r',
                              },
                'Limits': (-180, 180),
                'Label': 'Voltage [V]'
                },
    'Current': {'LineKwarg': {'color': 'b',
                              },
                'Limits': (-15, 15),
                'Factor': 1e6,
                'Label': 'Current [uA]'
                },
    'Position': {'LineKwarg': {'color': 'k',
                               'linestyle': 'dashed',
                               'linewidth': 0.5,
                               },
                 # 'Limits': (-5, 5),
                 'Label': 'Position [mm]'
                 },
    'Force': {'LineKwarg': {'color': 'g',
                            'linestyle': 'dashed',
                            'linewidth': 0.5,
                            },
              # 'Limits': (-5, 5),
              'Label': 'Force [N]'
              },
    'Acceleration': {'LineKwarg': {'color': 'orange',
                                   'linestyle': 'dashed',
                                   'linewidth': 0.5,
                                   },
                     'Limits': (-20, 20),
                     'Label': 'Acceleration [m/s^2]'
                     },
    'Velocity': {'LineKwarg': {'color': 'brown',
                               'linestyle': 'dashed',
                               'linewidth': 0.5,
                               },
                 'Limits': (-0.3, 0.3),
                 'Label': 'Velocity [m/s]'
                 },
    'Power': {'LineKwarg': {'color': 'purple',
                            },
              'Factor': 1e6,
              'Limits': (0, 1000),
              'Label': 'Power [uW]'},
}


dSel = dfData
#dSel = dfData.query("TribuId == 'SwTENG-RF2' ")

for ex, dExp in dSel.groupby('ExpId'):
    fig, (axtime, axpos) = plt.subplots(2, 1, figsize=(11, 7))
    for gn, df in dExp.groupby('RloadId'):
        # plot time traces
        AxsDict, _ = GenFigure(dfData=df.iloc[0].Data,
                               xVar='Time',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axtime)
        for index, r in df.iterrows():
            Data = r.Data
            for var, ax in AxsDict.items():
                if 'Factor' in VarColors[var]:
                    ptdata = Data[var] * VarColors[var]['Factor']
                else:
                    ptdata = Data[var]
                ax.plot(Data['Time'], ptdata, **VarColors[var]['LineKwarg'])
                ax.axvline(x=r.tTransition, color='y')
            ax.set_xlabel('Time')

        # plot position traces
        AxsDict, _ = GenFigure(dfData=df.iloc[0].Data,
                               xVar='Position',
                               PlotColumns=VarColors,
                               axisFactor=0.15,
                               ax=axpos)
        for index, r in df.iterrows():
            Data = r.Data
            for var, ax in AxsDict.items():
                if 'Factor' in VarColors[var]:
                    ptdata = Data[var] * VarColors[var]['Factor']
                else:
                    ptdata = Data[var]
                ax.plot(Data['Position'], ptdata, **VarColors[var]['LineKwarg'])
            ax.set_xlabel('Position')
            ax.set_xlim(0, 2)

        fig.suptitle(f'Experiment: {r.ExpId}, Tribu: {r.TribuId}, Rload: {r.RloadId}, Req: {r.Req}')
        fig.tight_layout()
        PDF.savefig(fig)
        plt.close(fig)
   # Guardar la figura como una imagen en la carpeta "images"
   #      image_file = f'./images/Experiment_{ex}_Rload_{gn}.png'
   #      fig.savefig(image_file)
   #      image_files.append(image_file)


# # Crear animación con las imágenes
# animation_file = 'animation.gif'
# with imageio.get_writer(animation_file, mode='I', fps=2) as writer:
#     for image_file in image_files:
#         image = imageio.imread(image_file)
#         writer.append_data(image)
#
# print(f'Animation saved as {animation_file}')
PDF.close()
