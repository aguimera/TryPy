import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from TryPy.PlotData import GenFigure

plt.close('all')

FileIn = '../DataSets/Cycles.pkl'
dfData = pd.read_pickle(FileIn)

dSel = dfData.query("TribuId == 'SwTENG-R'")

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

PDF = PdfPages('test.pdf')

for ex, dExp in dSel.groupby('ExpId'):
    fig, (axtime, axpos) = plt.subplots(2, 1, figsize=(11, 7))
    for gn, df in dExp.groupby('RloadId'):
        # plot time traces
        AxsDict, _ = GenFigure(dfData=df.loc[2, 'Data'],
                               xVar='Time',
                               PlotColumns=VarColors,
                               axisFactor=0.1,
                               ax=axtime)
        for index, r in df.iterrows():
            Data = r.Data
            for var, ax in AxsDict.items():
                if 'Factor' in VarColors[var]:
                    ptdata = Data[var] * VarColors[var]['Factor']
                else:
                    ptdata = Data[var]

                ax.plot(Data['Time'], ptdata, alpha=0.5, **VarColors[var]['LineKwarg'])
                ax.axvline(x=r.tTransition, color='y')
                ax.set_xlabel('Time')

        # plot position traces
        AxsDict, _ = GenFigure(dfData=df.loc[2, 'Data'],
                               xVar='Position',
                               PlotColumns=VarColors,
                               axisFactor=0.1,
                               ax=axpos)
        for index, r in df.iterrows():
            Data = r.Data
            for var, ax in AxsDict.items():
                if 'Factor' in VarColors[var]:
                    ptdata = Data[var] * VarColors[var]['Factor']
                else:
                    ptdata = Data[var]

                ax.plot(Data['Position'], ptdata, alpha=0.5, **VarColors[var]['LineKwarg'])
                ax.set_xlabel('Position')
                ax.set_xlim(0, 2)

        fig.suptitle(f'Experiment: {r.ExpId}, Tribu: {r.TribuId}, Rload: {r.RloadId}, Req: {r.Req}')
        fig.tight_layout()
        # fig.tight_layout(rect=[0.05, 0.05, 0.5, 0.95])
        fig.canvas.draw()
        PDF.savefig(fig, bbox_inches='tight')

PDF.close()
