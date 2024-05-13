# Import library
import numpy as np
from scipy.integrate import simpson
import pandas as pd


def ExtractCyclesByPos(dfData, ContactPosition=8, Latency=10e-3):

    dt = dfData.Time[dfData['Position'] < ContactPosition].diff()
    StartIds = np.where(dt > Latency)[0]
    StartIds = np.hstack((0, StartIds))
    Indexes = dt.index.values
    StartIndexes = Indexes[StartIds]
    EndIndexes = Indexes[StartIds - 1][1:]
    EndIndexes = np.hstack((EndIndexes, Indexes[-1]))

    # Calculate Duration
    # Calculate Maximum Duration
    nSampsCycle = EndIndexes - StartIndexes
    print('Cycles Samples', nSampsCycle)
    nSampsCycle = np.max(nSampsCycle)

    # Debug
    # Duration = dfData.Time[EndIndexs].values - dfData.Time[StartIndexs].values
    # print('Cycles Duration')
    # print(Duration)

    CyclesList = []
    for ic, st in enumerate(StartIndexes):
        # TODO parametrize this step
        # Set all cycles to same size
        ed = st + nSampsCycle
        if ed > dfData.shape[0]:
            ed = dfData.shape[0] - 1
        # Extract Cycle
        data = dfData[st:ed].copy()

        # Reset cycle time to zero
        data.reset_index(inplace=True, drop=True)
        data.loc[:, 'Time'] = data.Time.values - data.Time[0]

        Cycle = {'Data': data,  # Dataframe with recorded data
                 'Cycle': ic,  # Cycle number
                 'tStart': dfData.Time[st],  # Cycle Start time
                 'LocStart': dfData.Position[st],  # Cycle Start position
                 'tEnd': dfData.Time[ed],  # Cycle End time
                 'LocEnd': dfData.Position[ed],  # Cycle End position
                 'CycleDuration': dfData.Time[ed] - dfData.Time[st],  # Cycle Duration
                 }
        CyclesList.append(Cycle)

    return CyclesList

def FindTransitionTime(dfCycles, CurrentTh=None):

    for index, row in dfCycles.iterrows():
        if CurrentTh is None:
            IndHalf = int(row.Data.shape[0] / 2)
            dfCycles.loc[index, 'tTransition'] = row.Data.Time[IndHalf]
            dfCycles.loc[index, 'iTransition'] = IndHalf
            continue

    return dfCycles


def ExtractCycles(dfData, ContactPosition=8, ContactForce=None, Latency=10e-3, CurrentTh=None):
    """
    Extracts cycles from the given dataframe based on the specified ContactPosition or ContactForce.
    Calculates various parameters for each cycle and returns a list of dictionaries containing the cycle data.

    Parameters:
    - dfData: DataFrame, the input data
    - ContactPosition: int, optional, the position for contact detection
    - ContactForce: float, optional, the force for contact detection
    - Latency: float, the latency threshold
    - CurrentTh: float, optional, the current threshold for transition time calculation

    Returns:
    - CyclesList: list of dicts, containing data for each cycle
    """

    # Calculate Contact Position
    if ContactPosition is not None:
        dt = dfData.Time[dfData['Position'] < ContactPosition].diff()
        StartInds = np.where(dt > Latency)[0]
        StartInds = np.hstack((0, StartInds))
        Indexs = dt.index.values
        StartIndexs = Indexs[StartInds]
        EndIndexs = Indexs[StartInds - 1][1:]
        EndIndexs = np.hstack((EndIndexs, Indexs[-1]))
    elif ContactForce is not None:
        dt = dfData.Time[dfData['Force'] > ContactForce].diff()
        StartInds = np.where(dt > Latency)[0]
        StartInds = np.hstack((0, StartInds))
        Indexs = dt.index.values
        StartIndexs = Indexs[StartInds]
        EndIndexs = Indexs[StartInds - 1][1:]
        EndIndexs = np.hstack((EndIndexs, Indexs[-1]))
    else:
        print('Please specify ContactForce or ContactPosition')
        return None

    # Calculate Maximum Duration
    nSampsCycle = EndIndexs - StartIndexs
    print('Cycles Samples', nSampsCycle)
    nSampsCycle = np.max(nSampsCycle)

    # Debug
    # Duration = dfData.Time[EndIndexs].values - dfData.Time[StartIndexs].values
    # print('Cycles Duration')
    # print(Duration)

    CyclesList = []
    for ic, st in enumerate(StartIndexs[:-1]):
        # TODO parametrize this step
        # Set all cycles to same size
        ed = st + nSampsCycle
        if ed > dfData.shape[0]:
            ed = dfData.shape[0]-1
        # Extract Cycle
        data = dfData[st:ed].copy()

        # Reset cycle time to zero
        data.reset_index(inplace=True, drop=True)
        data.loc[:, 'Time'] = data.Time.values - data.Time[0]


        if CurrentTh is None:
            IndHalf = int(data.shape[0] / 2)
        else:
            negative_values = data[data.Current < 0].copy()
            positive_values = data[(data.Current > 0) & (data.Current > CurrentTh)].copy()
            negative_values['order'] = negative_values.index
            positive_values['order'] = positive_values.index

            combined_values = pd.concat([negative_values, positive_values])
            combined_values = combined_values.sort_values(by='order')

            combined_values = combined_values.drop(columns=['order'])
            combined_values = combined_values.dropna(axis=0, subset=['Current'])
            original_index = combined_values.index

            combined_values_reset = combined_values.reset_index(drop=True)

            idx_reset = combined_values_reset.index[
                (combined_values_reset.Current >= 0) & (combined_values_reset.Current.shift(-1) < 0)].min()

            combined_values_reset.index = original_index
            # Obtener el índice correcto
            hindexes = combined_values_reset.iloc[idx_reset].name
            if hindexes == 0:
                print('No Current Threshold crossed')
                IndHalf = int(data.shape[0] / 2)
            else:
                IndHalf = hindexes
            print(f'Time Transition {data.Time[IndHalf]} {IndHalf}')
        imax = data.Current.idxmax()
        imin = data.Current.idxmin()
        Cycle = {'Data': data,  # Dataframe with recorded data
                 'Cycle': ic,  # Cycle number
                 'tStart': dfData.Time[st],  # Cycle Start time
                 'PosStart': dfData.Position[st],  # Cycle Start position
                 'tEnd': dfData.Time[ed],  # Cycle End time
                 'PosEnd': dfData.Position[ed],  # Cycle End position
                 'IMax': data.Current[imax],  # Max current
                 'PosIMax': dfData.Position[imax],  # Position of max current
                 'IMin': data.Current[imin],  # Min current
                 'PosIMin': dfData.Position[imin],  # Position of min current
                 'VMax': data.Voltage.max(),  # Max voltage
                 'VMin': data.Voltage.min(),  # Min voltage
                 'tTransition': data.Time[IndHalf],  # Transition time between positive and negative current
                 'PosPMax': dfData.Power[:IndHalf].max(),  # Max positive power
                 'NegPMax': dfData.Power[IndHalf:].max(),  # Max negative power
                 'PosEnergy': simpson(y=data.Power[:IndHalf], x=data.Time[:IndHalf]),  # Positive energy
                 'NegEnergy': simpson(y=data.Power[IndHalf:], x=data.Time[IndHalf:]),  # Negative energy
                 'Energy': simpson(y=data.Power, x=data.Time),  # Negative energy
                 }
        CyclesList.append(Cycle)

    return CyclesList
