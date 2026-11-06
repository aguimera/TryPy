import pickle
import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import numpy as np

# 1. Open a file dialog window to select the .pkl file
root = tk.Tk()
root.withdraw()  # Hide the main tkinter root window

file_path = filedialog.askopenfilename(
    title="Select Voltage Pickle File",
    filetypes=[("Pickle Files", "*.pkl"), ("All Files", "*.*")],
)

# Check if a file was selected
if not file_path:
  print("No file selected. Exiting program.")
else:
  # 2. Load the pickle file containing voltage information
  with open(file_path, "rb") as f:
    data = pickle.load(f)

  # Convert data to a numpy array (adjust if your data is a dictionary or pandas DataFrame)
  voltages = np.array(data)

  # 3. Convert voltage to current using the conversion factor (1.05e-7)
  conversion_factor = 1.05e-7
  current_amperes = voltages * conversion_factor

  # 4. Convert current from Amperes to nanoamperes (nA) (1 A = 10^9 nA)
  current_nA = current_amperes * 1e9

  # 5. Plot the results in nA scale
  plt.figure(figsize=(10, 5))
  plt.plot(current_nA, color="royalblue", linewidth=1.5, label="Current")

  plt.title("Current Measurement (nA Scale)", fontsize=14)
  plt.xlabel("Data Points / Time Index", fontsize=12)
  plt.ylabel("Current (nA)", fontsize=12)
  plt.grid(True, linestyle="--", alpha=0.6)
  plt.legend(loc="upper right")
  plt.tight_layout()

  # Display the plot
  plt.show()