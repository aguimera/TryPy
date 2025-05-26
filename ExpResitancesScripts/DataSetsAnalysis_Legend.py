from cProfile import label
from math import ceil

import numpy as np
import pandas as pd
import os
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.integrate import simpson
# from test.handles import Cycle

from TryPy.PlotData import PlotScalarValues, GenFigure

# %% Load data
DataFolder = 'S:/TriboMedData/CharacterizationData/TENGData/RenyunTENG/ExpElectrodes/'
ExpDef = DataFolder + 'RawData/Experiments.ods' #Excel name to use
TribuId = "'RenyunTENGRC'"

#Takes the pkl generated in LoadExperiments and process it
FileIn = DataFolder + 'DataSets/Cycles-ExperimentsNewElectrodes.pkl'
dfData = pd.read_pickle(FileIn)

#Generate new pdf report called DataSetsAnalysis
PDF = PdfPages(DataFolder + 'Reports/DataSetsAnalysis.pdf')


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
# Here you specify which variables will be plotted
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
dSel = dfData.query("TribuId == " + TribuId)
fig, ax = plt.subplots()
sns.lineplot(data=dSel,
             x='ExpId',
             y='PositiveEnergy',
             ax=ax,
             color= 'black',
             label='PositiveEnergy')
sns.lineplot(data=dSel,
             x='ExpId',
             y='NegativeEnergy',
             ax=ax,
             color=(0.5, 0.5, 0.5), #dark gray colour
             label='NegativeEnergy')
sns.lineplot(data=dSel,
             x='ExpId',
             y='Energy',
             ax=ax,
             color=(0.8, 0.8, 0.8),  # Medium gray color
             label='Energy')
# ax.set_xscale('log')
# ax.set_yscale('log')
ax.set_xlabel('ExpId')
ax.set_ylabel('Energy (J)')
fig.suptitle(r.TribuId)
fig = ax.get_figure()
# fig.suptitle(f'Req: {r.Req / 1e6:.2f} MΩ, {r.TribuId}')
ax.legend()
PDF.savefig(fig)

# Gráfica para Energia
# Obtener los nombres de los diferentes valores de ExpId
# Configurar el gráfico
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Energy Variability')
# Trazar los puntos para PosEnergy, NegEnergy y Energy en función de Req
sns.scatterplot(data=dfData, x='ExpId', y='PositiveEnergy', ax=ax, label='PosEnergy', color='blue')
sns.scatterplot(data=dfData, x='ExpId', y='NegativeEnergy', ax=ax, label='NegEnergy', color='red')
sns.scatterplot(data=dfData, x='ExpId', y='Energy', ax=ax, label='Energy', color='green')
ax.set_xlabel('ExpId')
ax.set_ylabel('Energy (J)')
fig = ax.get_figure()
ax.legend()
# plt.xticks(rotation=45)  # Rotar las etiquetas del eje x para una mejor legibilidad
plt.tight_layout()
PDF.savefig(fig)

# Gráfica para Energia
# Obtener los nombres de los diferentes valores de ExpId
# Configurar el gráfico
fig, ax = plt.subplots(figsize=(10, 6))
fig.suptitle('Current Variability')
# Trazar los puntos para PosEnergy, NegEnergy y Energy en función de Req
sns.scatterplot(data=dfData, x='ExpId', y='CurrentMax', ax=ax, label='PosCurrent', color='blue')
sns.scatterplot(data=dfData, x='ExpId', y='CurrentMin', ax=ax, label='NegCurrent', color='red')
ax.set_xlabel('ExpId')
ax.set_ylabel('Current(A)')
fig = ax.get_figure()
ax.legend()
# plt.xticks(rotation=45)  # Rotar las etiquetas del eje x para una mejor legibilidad
plt.tight_layout()
PDF.savefig(fig)

# %% Plot experiment time traces

VarColors = {
    'Voltage': {'LineKwarg': {'color': 'red',
                'linestyle': 'solid'
                              },
                # 'Limits': (-3, 5),
                'Label': 'Voltage [V]'
                },
    'Current': {'LineKwarg': {'color': 'green',
                 'linewidth': 0.3,
                # 'linestyle': 'dashed'
                              },
                # 'Limits': (-15, 15),
                'Factor': 1e6,
                'Label': 'Current [uA]'
                },
    'Position': {'LineKwarg': {'color': 'gray',
                               'linestyle': 'dashed',
                               'linewidth': 0.5,
                               },
                 # 'Limits': (-5, 5),
                 'Label': 'Position [mm]'
                 },
    # 'Force': {'LineKwarg': {'color': 'g',
    #                         'linestyle': 'dashed',
    #                         'linewidth': 0.5,
    #                         },
    #           # 'Limits': (-5, 5),
    #           'Label': 'Force [N]'
    #           },
    # 'Acceleration': {'LineKwarg': {'color': 'orange',
    #                                'linestyle': 'dashed',
    #                                'linewidth': 0.5,
    #                                },
    #                  'Limits': (-20, 20),
    #                  'Label': 'Acceleration [m/s^2]'
    #                  },
    # 'Velocity': {'LineKwarg': {'color': 'brown',
    #                            'linestyle': 'dashed',
    #                            'linewidth': 0.5,
    #                            },
    #              'Limits': (-0.3, 0.3),
    #              'Label': 'Velocity [m/s]'
    #              },
    # 'Power': {'LineKwarg': {'color': 'purple',
    #                         },
    #           'Factor': 1e6,
    #           'Limits': (0, 1000),
    #           'Label': 'Power [uW]'},

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
        legend_elements = [] # modify

        for index, r in df.iterrows():
            Data = r.Data

            for var, ax in AxsDict.items():

                if 'Factor' in VarColors[var]:
                    ptdata = Data[var] * VarColors[var]['Factor']
                else:
                    ptdata = Data[var]
                ax.plot(Data['Time'], ptdata, **VarColors[var]['LineKwarg'])
                #Plot the line that separates the positive/negative peaks
                #ax.axvline(x=r.tTransition, color='y')
                ax.set_xlabel('Time[s]')

        line = axtime.plot([], [], label=VarColors['Voltage']['Label'], **VarColors['Voltage']['LineKwarg'])[0]  # modify
        legend_elements.append(line)  # modify
        line = axtime.plot([], [], label=VarColors['Current']['Label'], **VarColors['Current']['LineKwarg'])[0]  # modify
        legend_elements.append(line)  # modify
        line = axtime.plot([], [], label=VarColors['Position']['Label'], **VarColors['Position']['LineKwarg'])[0]  # modify
        legend_elements.append(line)  # modify

        axtime.legend()  # modify



        # # plot position traces
        # AxsDict, _ = GenFigure(dfData=df.iloc[0].Data,
        #                        xVar='Position',
        #                        PlotColumns=VarColors,
        #                        axisFactor=0.15,
        #                        ax=axpos)
        # for index, r in df.iterrows():
        #     Data = r.Data
        #     for var, ax in AxsDict.items():
        #         if 'Factor' in VarColors[var]:
        #             ptdata = Data[var] * VarColors[var]['Factor']
        #         else:
        #             ptdata = Data[var]
        #         ax.plot(Data['Position'], ptdata, **VarColors[var]['LineKwarg'])
        #     ax.set_xlabel('Position')
        #     ax.set_xlim(0, 2)
        #

        fig.suptitle(f'Experiment: {r.ExpId}, Tribu: {r.TribuId}, Rload: {r.RloadId}, Req: {r.Req}')
        fig.tight_layout()
        PDF.savefig(fig)
        plt.close(fig)

#%% Pulse Width Analysis

# # Peaks detection Plot
# dSel = dfData
# for exp_id, dExp in dSel.groupby('ExpId'):
#     # Crear figura con 2 filas y 3 columnas de subplots
#     fig, axs = plt.subplots(2, 3, figsize=(15, 10))  # Puedes ajustar el tamaño con figsize
#     for gn, df in dExp.groupby('RloadId'):
#         # Acceder a cada subplot con axs[fila][columna]
#         C0=0
#         data = df.loc[df.Cycle[0], 'Data']
#         axs[0, 0].plot(data['Time'],data['Current'])  # Fila 0, Columna 0
#         axs[0, 0].plot(df['CurrentMaxTime'], df['CurrentMax'])  # Fila 0, Columna 0
#
#         # Cend = len(dfData['Cycle'])
#         axs[0, 1].plot([], [])  # Fila 0, Columna 1
#         axs[0, 1].plot([], [])  # Fila 0, Columna 1
#
#         axs[0, 2].plot([], [])  # Fila 0, Columna 2
#         axs[1, 0].plot([], [])  # Fila 1, Columna 0
#         axs[1, 1].plot([], [])  # Fila 1, Columna 1
#         axs[1, 2].plot([], [])  # Fila 1, Columna 2
#
#     # Mostrar gráfico
# plt.show()
# fig.tight_layout()
# PDF.savefig(fig)
# plt.close(fig)
#
#


#Peaks Values vs Cycle Plot Analysis
dSel = dfData
for exp_id, dExp in dSel.groupby('ExpId'):
    fig, ax = plt.subplots()
    ax.scatter(dExp['Cycle'], dExp['PositivePulseWidth'], label='Pos Peak Width', color='blue', marker='o')
    ax.scatter(dExp['Cycle'], dExp['NegativePulseWidth'], label='Neg Peak Width', color='red', marker='o')
    ax.set_xlabel('Cycle Number')
    ax.set_ylabel('Pulse Widths (s)')
    ax.set_title(f'Pulse Width at Half Maximum - ExpId: {exp_id}')
    ax.legend()
    fig.tight_layout()
    PDF.savefig(fig)
    plt.close(fig)



#%% Statistical Analysis Plots
fig, ax = plt.subplots()
sns.stripplot(data=dfData,
              x='Req',
              y='Energy',
              hue='TribuId',
              ax=ax,
              )
fig.suptitle('Strip Plot')
PDF.savefig(fig)

fig, ax = plt.subplots()
sns.scatterplot(data=dfData,
                  x='Req',
                  y='Energy',
                  hue='TribuId',
                  ax=ax,
                  )
fig.suptitle('Scatter Plot')
PDF.savefig(fig)

fig, ax = plt.subplots()
sns.boxplot(data=dfData,
              x='TribuId',
              y='Energy',
              #order=['SwTENG-R', 'SwTENG-RF2', 'SwTENG-RF3'],
              #hue='Comments',
              ax=ax,
              )
fig.suptitle('Box Plot')
PDF.savefig(fig)


#%% Save Plots as Images
    #Guardar la figura como una imagen en la carpeta "images"
    # image_file = f'./images/Experiment_{ex}_Rload_{gn}.png'
    # fig.savefig(image_file)
    # image_files.append(image_file)


#Create images animation
# animation_file = 'animation.gif'
# with imageio.get_writer(animation_file, mode='I', fps=2) as writer:
#     for image_file in image_files:
#         image = imageio.imread(image_file)
#         writer.append_data(image)
#
# print(f'Animation saved as {animation_file}')

PDF.close()