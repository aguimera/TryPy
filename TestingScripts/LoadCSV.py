import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIG ---
files = ["Isc PTFE gun vsd Nylon 6 2 uA x1.csv", "Isc PTFE vs Nylon 6 uncharged range 20 nA x10.csv"]
time_col = "Time (s)"
value_col = "Current (A)"
# -------------

signals = [pd.read_csv(f, sep=",", decimal=".") for f in files]

plt.figure(figsize=(10, 6))

for i, sig in enumerate(signals):
    plt.plot(sig[time_col], sig[value_col], label=f" {i+1}")

plt.title("Collapsed Signals",fontsize=18)
plt.xlabel("Time (s)",fontsize=16)
plt.ylabel("Current (A)",fontsize=16)
plt.legend(fontsize=16)
plt.tick_params(axis='both', labelsize=16)  # tamaño números en ejes
plt.tight_layout()
plt.show()
