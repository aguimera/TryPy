import pandas as pd
import os
import numpy as np
import re
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
# Merge CSV and xlsx into a single file named DAQ and motor
# Save the file names into Experiments excels
# Go to LoadExperiments and load excels of experiment metadata containing merged file names

def LTIME_to_seconds(LTIME):
    
    conversor = {"h": 3600,
                 "m": 60,
                 "s": 1,
                 "ms": 1e-3,
                 "us": 1e-6,
                 "ns": 1e-9}

    units = re.split(r'\d+', LTIME)[1:]
    numbers_str = re.findall(r'\d+', LTIME)
    numbers = [int(number) for number in numbers_str]
    
    total_time = 0

    for number, unit in zip(numbers, units):
        total_time += number * conversor[unit]
    
    return total_time

def sort_function(string):
    return int(string.split("_")[-1].split(".")[0])


def CSV_merge(folder_path: str, save_path_folder: str, filename: str):
    files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    if not files:
        return

    files.sort(key=sort_function)

    # Create an empty DataFrame
    combined_DataFrame = pd.DataFrame()

    # Iterate the CSV files found in the folder path
    print("Merging...")
    for file in files:
        # Read CSV
        df = pd.read_csv(os.path.join(folder_path, file), sep=';')

        print(file)

        # Concatenate CSV file
        combined_DataFrame = pd.concat([combined_DataFrame, df], ignore_index=True)

    # Save concatenated DataFrame
    combined_DataFrame.to_csv(os.path.join(save_path_folder, filename + ".csv"), index=False, sep=';')

    print("Data saved to location:", os.path.join(save_path_folder, filename + ".csv"))

    return os.path.join(save_path_folder, filename + ".csv")

def Excel_merge(folder_path: str, save_path_folder: str, filename: str):
    files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx')]

    if not files:
        return

    files.sort()

    # Create an empty DataFrame
    combined_DataFrame = pd.DataFrame()

    # Iterate the Excel files found in the folder path
    print("Merging...")
    for file in files:
        # Read Excel
        df = pd.read_excel(os.path.join(folder_path, file))

        print(file)

        # Concatenate CSV file
        combined_DataFrame = pd.concat([combined_DataFrame, df], ignore_index=True)

    # Save concatenated DataFrame
    combined_DataFrame.to_excel(os.path.join(save_path_folder, filename + ".xlsx"), index=False)

    print("Data saved to location:", os.path.join(save_path_folder, filename + ".xlsx"))

    return os.path.join(save_path_folder, filename + ".xlsx")


if __name__ == "__main__":

    # Get file save location from user:
    print("Please provide a save location for incoming data.")
    root = tk.Tk()
    root.withdraw()  # Amaga la finestra princial de tkinter
    root.lift()  # Posa la finestra emergent en primer pla
    root.attributes('-topmost', True)  # La finestra sempre al davant

    # Carpeta con la lista de archivos CSV y Excel a combinar
    carpeta = filedialog.askdirectory()

    if carpeta:
        carpeta = carpeta.replace("/", "\\")

        CSV_path = CSV_merge(folder_path=carpeta, save_path_folder=carpeta, filename="Motor_01")
        Excel_path = Excel_merge(folder_path=carpeta, save_path_folder=carpeta, filename="DAQ_01")
        df = pd.read_csv(CSV_path, sep=';')
        df_DAQ = pd.read_excel(Excel_path)

        time_array = np.empty((df.shape[0],))

        for index, row in df.iterrows():
            time_array[index] = LTIME_to_seconds(row["Time(s)"])

        time_array -= time_array[0]

        y1 = df['MC SW Overview - Actual Position(mm)'].values
        y2 = df['MC SW Force Control - Measured Force(N)'].values
        y3 = df['MC SW Force Control - Target Force(N)'].values

        # Crear figura y primer eje (Y1 - izquierda)
        fig, ax1 = plt.subplots(figsize=(8, 5))
        ax1.plot(time_array, y1, 'r-', label='Actual Position(mm)')
        ax1.set_ylabel('Actual Position(mm)', color='r')
        ax1.tick_params(axis='y', labelcolor='r')

        # Segundo eje (Y2 - derecha)
        ax2 = ax1.twinx()
        ax2.plot(time_array, y2, 'b', label='Measured Force(N)')
        ax2.set_ylabel('Measured Force(N)', color='b')
        ax2.tick_params(axis='y', labelcolor='b')

        # Tercer eje (Y3 - también derecha, pero desplazado)
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("outward", 60))  # Desplazar eje 60 px a la derecha
        ax3.plot(time_array, y3, 'g', label='Target Force(N)')
        ax3.set_ylabel('Target Force(N)', color='g')
        ax3.tick_params(axis='y', labelcolor='g')

        # Opcional: ocultar marco duplicado del eje
        ax3.spines["right"].set_visible(True)

        # Eje X compartido
        ax1.set_xlabel('Time(s)')

        # Título
        plt.title("LinMot data")
        plt.tight_layout()
        plt.show()

    else:
        print("Canceled")