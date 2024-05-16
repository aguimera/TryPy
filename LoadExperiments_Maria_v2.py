
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages



mpl.use("QtAgg")
plt.close('all')
plt.ion()



dfData = pd.read_excel('ExperimentsReultsRawrGOyRT1_0.xlsx')
#dfData = pd.read_excel('ExperimentsReultsRawrGOyt1_500.xlsx')

# Definir la variable de tiempo
XVar = 'Time'

# Generar el gráfico
fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(dfData[XVar], dfData['Voltage rGO'], label='Electrode')
ax.plot(dfData[XVar], dfData['Voltage R'], label=' 10 kOhm Resistance')
ax.set_xlabel(XVar)
ax.set_ylabel('Voltage (V)')
ax.set_xlabel('Time (s)')

ax.legend()

fig.suptitle('Exp1')
fig.tight_layout()

# Guardar el gráfico en un archivo PDF
with PdfPages('Exp1_Graphs.pdf') as PDF:
    PDF.savefig(fig)

plt.ion()