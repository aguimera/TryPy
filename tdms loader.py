
import numpy as np
import matplotlib.pyplot as plt
from nptdms import TdmsFile
from tkinter import Tk, filedialog

# Select the TDMS file
root = Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Select a TDMS file",
    filetypes=[("TDMS files", "*.tdms"), ("All files", "*.*")]
)

root.destroy()

if not file_path:
    print("No file selected.")
    raise SystemExit

# Load TDMS data
tdms_file = TdmsFile.read(file_path)

# Display available groups and channels
for group in tdms_file.groups():
    print(f"\nGroup: {group.name}")
    for channel in group.channels():
        print(f"  Channel: {channel.name}")

# Select the first channel of the first group
group = tdms_file.groups()[0]
channel = group.channels()[0]

voltage = channel[:]

# Get sampling rate from TDMS properties, if available
properties = channel.properties

if "wf_increment" in properties:
    dt = properties["wf_increment"]
    time = np.arange(len(voltage)) * dt
else:
    # Set your sampling rate here if it is not stored in the file
    sampling_rate = 10000  # Hz (change to your actual value)
    time = np.arange(len(voltage)) / sampling_rate

# Plot raw voltage data
plt.figure(figsize=(12, 5))
plt.plot(time, voltage, linewidth=0.8)

plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title(f"Raw Voltage Data: {channel.name}")

# Fixed voltage axis limits
plt.ylim(-10, 10)

plt.grid(True)
plt.tight_layout()
plt.show()
