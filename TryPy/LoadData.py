import os
import numpy as np
import pandas as pd
from nptdms import TdmsFile
from scipy.signal import freqs_zpk
from scipy.fft import fft, rfft
from scipy.fft import fftfreq, rfftfreq
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

# %% Rename Raw Data columns
MotColumnRenames = {
    'Time(s)': 'Time',
    'MC SW Overview - Actual Position(mm)': 'Position',
    'MC SW Force Control - Measured Force(N)': 'Force',
    'MC SW Force Control - Target Force(N)': 'TargetForce',
    'MC SW Overview - Actual Velocity(m/s)': 'Velocity',
    'MC SW Force Control - Actual Acceleration(m/s^2)': 'Acceleration',
}

DQAColumnRenames = {
    'Input 0': 'Voltage',
    'Unnamed: 1': 'Time',
    'Original Data': 'Voltage DC',
    'AC Signal': 'Voltage with Trend',
    'AC with Trend': 'Voltage',
}

#%% Load Motor Raw Data
def LoadMotorFile(MotorFile):
    """
    LoadMotorFile reads a CSV file and processes it to remove non-defined columns and rename columns.
    It takes a single parameter MotorFile, which is the path to the CSV file.
    Return:
    - dfMOT data frame
    """
    dfMOT = pd.read_csv(MotorFile,
                        header=0,
                        index_col=False,
                        delimiter=',',
                        decimal='.')
    # drop Non-defined columns
    dropcols = []
    for col in dfMOT.columns:
        if col not in MotColumnRenames.keys():
            dropcols.append(col)
    dfMOT = dfMOT.drop(columns=dropcols)
    # rename columns
    dfMOT = dfMOT.rename(columns=MotColumnRenames)
    # Estimate Velocity
    if 'Velocity' not in dfMOT.columns:
        dfMOT['Velocity'] = (dfMOT.Position.diff() / 1000) / dfMOT.Time.diff()
    # Estimate Acceleration
    if 'Acceleration' not in dfMOT.columns:
        dfMOT['Acceleration'] = dfMOT.Velocity.diff() / dfMOT.Time.diff()
    return dfMOT

#%% Load DAQ Raw Data
def LoadDAQFile(DaqFile):
    """
    A function to load a DAQ file and return a DataFrame based on the file type.
    Parameters:
    - DaqFile: the file path of the DAQ file to be loaded
    Return:
    - dfDAQ: a DataFrame containing the DAQ data
    - None if the file type is not recognized
    """
    if DaqFile.endswith('.tdms'):
        tdms_file = TdmsFile.read(DaqFile)
        dfDAQ = tdms_file.as_dataframe(time_index=True,
                                       scaled_data=False)
        dfDAQ.reset_index(inplace=True)
        # dfDAQ = dfDAQ.iloc[:, :2]
        dfDAQ = dfDAQ.set_axis(['Time', 'Voltage'], axis=1)
        return dfDAQ
    elif DaqFile.endswith('.xlsx'):
        daqf = pd.ExcelFile(DaqFile)
        sheets = daqf.sheet_names

        # Check if there's more than one sheet
        if len(sheets) > 1:
            sheet_to_use = sheets[1]
        else:
            print(f"⚠️ Only one sheet found in '{DaqFile}'. Using the first one.")
            sheet_to_use = sheets[0]

        dfDAQ = pd.read_excel(DaqFile, sheet_name=sheet_to_use)

        # Optionally rename columns if DQAColumnRenames is defined
        if 'DQAColumnRenames' in globals():
            dfDAQ = dfDAQ.rename(columns=DQAColumnRenames)
        return dfDAQ
    elif DaqFile.endswith('.csv'):
        dfDAQ = pd.read_csv(DaqFile,
                            header=0,
                            index_col=False,
                            delimiter=',',
                            decimal='.')
        # drop Non-defined columns
        dropcols = []
        for col in dfDAQ.columns:
            if col not in DQAColumnRenames.keys():
                dropcols.append(col)
        dfDAQ = dfDAQ.drop(columns=dropcols)
        # rename columns
        dfDAQ = dfDAQ.rename(columns=DQAColumnRenames)
        return dfDAQ
    else:
        print(f'❌ File {DaqFile} not recognized')
        return None

#%%  Loads data files, calculates sampling rates, interpolates data, and calculates voltage, current, and power.
def Loadfiles(ExpDef):
    """
    Parameters:
    - ExpDef: Experiment definition containing file paths, gain, and resistance values.
    Returns:
    - dfData: DataFrame containing loaded and processed data.
    """
    r = ExpDef
    if not os.path.isfile(r.DaqFile):
        print(f'File {r.DaqFile} not found')
        return None
    if not os.path.isfile(r.MotorFile):
        print(f'File {r.MotorFile} not found')
        return None

    # Load DAQ file
    dfDAQ = LoadDAQFile(r.DaqFile)

    # Load Motor file
    dfMOT = LoadMotorFile(r.MotorFile)

    # Motor sampling Rate
    nSampsMotor = dfMOT.Time.size
    MotFs = 1 / dfMOT.Time.diff().mean()
    print(f'Motor sampling rate: {MotFs}')

    # DAQ sampling rate
    if 'Time' in dfDAQ.columns:
        nSampsDAQ = dfDAQ.Voltage.size
        dt=dfDAQ.Time.diff().mean() # dt entre dos muestras de tiempo, tiempo entre muestras
        DaqFs = 1 / dt #in Hz
        print(f'Found DAQ sampling rate: {DaqFs}')
    else:
        nSampsDAQ = dfDAQ.Voltage.size
        DaqFs = nSampsDAQ / (1 / MotFs * nSampsMotor)
        print(f'Calculated DAQ sampling rate: {DaqFs}')
        dfDAQ['Time'] = np.arange(0, nSampsDAQ) / DaqFs

    if nSampsDAQ>nSampsMotor:
        # Interpolate Motor Data
        dfData = dfDAQ
        for col in dfMOT.columns:
            if col == 'Time':
                continue
            dfData[col] = np.interp(dfData.Time, dfMOT.Time, dfMOT[col])

    elif nSampsDAQ<nSampsMotor:
        # Interpolate DAQ Data
        dfData = dfMOT
        for col in dfDAQ.columns:
            if col == 'Time':
                continue
            dfData[col] = np.interp(dfData.Time, dfDAQ.Time, dfDAQ[col])

    #%% Signal Filtering
    # TODO parametrize this
    window_size = 9  # Tamaño de la ventana del filtro
    # dfData['SmoothVoltages'] = dfData['Voltage'].rolling(window=window_size).median()
    # dfData['SmoothVoltage'] = dfData['Voltage'].rolling(window=window_size).mean()

    fourier=fft((dfData['Voltage']))
    N = len(dfData['Voltage'])
    normalize = N / 2
    freq_components=fftfreq(len(dfData['Voltage']),1/DaqFs)
    norm_amplitude = np.abs(fourier)/normalize


    plt.plot(freq_components, norm_amplitude)
    plt.xlabel('Frequency[Hz]')
    plt.ylabel('Amplitude')
    plt.title('Spectrum')
    plt.show()

    dfData['SmoothVoltage'] = dfData['Voltage']  # No hace nada, es para quitar el filtro y que funcione el código
    # Plot the results

    #Calcula Corriente a través de un RC
    #r.Ceq = r.Ceq / 1e6  # Pasa de microF a F
    # i = np.zeros_like(dfData.Voltage)
    # dt=dfDAQ.Time.diff().mean()
    # #alpha = (r.Req * r.Ceq) / (r.Req * r.Ceq + dt)
    # #beta = r.Ceq / (r.Req * r.Ceq + dt)
    # for n in range(1, len(dfData.Voltage)):
    #     i[n] = alpha * i[n - 1] + beta * (dfData.Voltage[n] - dfData.Voltage[n - 1])  # Differential equation solved as discrete

    #%% Adds Voltage, Current and Power
    dfData['VoltageAcq'] = dfData.Voltage
    dfData['Voltage'] = dfData['SmoothVoltage'] / r.Gain
    dfData['Current'] = dfData.Voltage / r.Req #Calculates Current Through an R
    dfData['Power'] = dfData.Current * dfData.Voltage
    #dfData['CurrentRC'] = i #Calculates Current Through an RC

    return dfData
