
import numpy as np
import matplotlib.pyplot as plt

from nptdms import TdmsFile
from scipy.signal import iirnotch, filtfilt
from scipy.signal import iircomb
from tkinter import Tk, filedialog, messagebox


# ==========================================
# CONFIGURACIÓN
# ==========================================

FREQUENCY = 50       # Frecuencia a eliminar (Hz)
QUALITY_FACTOR = 30  # Factor de calidad del filtro

# Intervalos que queremos eliminar (segundos)
CUT_INTERVALS = [
    (30, 73),
    (103, 131)
]


# ==========================================
# CARGAR ARCHIVO TDMS
# ==========================================

root = Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Seleccionar archivo TDMS",
    filetypes=[("Archivos TDMS", "*.tdms")]
)

if not file_path:
    print("No se ha seleccionado ningún archivo.")
    raise SystemExit

tdms_file = TdmsFile.read(file_path)

# Seleccionar automáticamente el primer canal disponible
channels = []

for group in tdms_file.groups():
    for channel in group.channels():
        channels.append(channel)

if not channels:
    raise ValueError("El archivo TDMS no contiene canales.")

print("Canales disponibles:")

for i, channel in enumerate(channels):
    print(i, channel.path)

# Elegir canal
channel_index = 0

if len(channels) > 1:
    channel_index = int(input(
        "Introduce el número del canal que quieres analizar: "
    ))

channel = channels[channel_index]
signal = channel[:]

# ==========================================
# FRECUENCIA DE MUESTREO
# ==========================================

properties = channel.properties

if "wf_increment" in properties:
    dt = properties["wf_increment"]
    fs = 1 / dt
elif "sampling_rate" in properties:
    fs = properties["sampling_rate"]
else:
    raise ValueError(
        "No se encuentra la frecuencia de muestreo "
        "en las propiedades del canal."
    )

signal = np.asarray(signal, dtype=float)

time = np.arange(len(signal)) / fs

print(f"Frecuencia de muestreo: {fs} Hz")
print(f"Número de muestras: {len(signal)}")
print(f"Duración: {time[-1]:.2f} segundos")


# ==========================================
# 1. GRAFICAR RAW DATA
# ==========================================

plt.figure(figsize=(14, 5))

plt.plot(time, signal, linewidth=0.7)

plt.title("Raw Data")
plt.xlabel("Tiempo (s)")
plt.ylabel("Amplitud")
plt.xlim(0,40)
plt.grid(True)

plt.tight_layout()
plt.show()


# ==========================================
# 2. APLICAR FILTRO NOTCH DE 50 Hz
# ==========================================

if fs <= 2 * FREQUENCY:
    raise ValueError(
        "La frecuencia de muestreo debe ser superior a 100 Hz."
    )

b, a = iircomb(
    FREQUENCY,
    QUALITY_FACTOR,
    ftype='notch',
    fs=30000
)

filtered_signal = filtfilt(b, a, signal)


# ==========================================
# 3. GRAFICAR SEÑAL FILTRADA
# ==========================================

plt.figure(figsize=(14, 5))

plt.plot(time, filtered_signal, linewidth=0.7)

plt.title("Señal filtrada - Notch 50 Hz")
plt.xlabel("Tiempo (s)")
plt.ylabel("Amplitud")
plt.grid(True)
plt.xlim(0,40)

plt.tight_layout()
plt.show()


# ==========================================
# 4. ELIMINAR LOS INTERVALOS
# ==========================================

mask = np.ones(len(time), dtype=bool)

for start, end in CUT_INTERVALS:
    mask &= ~((time >= start) & (time < end))

# Señal restante
cut_signal = filtered_signal[mask]
cut_time_original = time[mask]


# ==========================================
# 5. CONSTRUIR EJE TEMPORAL COMPRIMIDO
# ==========================================

# Quitamos los intervalos y juntamos los segmentos
cut_time = cut_time_original.copy()

removed_duration = 0

for start, end in CUT_INTERVALS:

    cut_time[cut_time_original >= end] -= (
        end - start
    )

    removed_duration += end - start


# ==========================================
# FFT - RAW DATA
# ==========================================

# Número de muestras
N = len(signal)

# FFT de la señal original
fft_values = np.fft.rfft(signal)

# Frecuencias correspondientes
frequencies = np.fft.rfftfreq(N, d=1/fs)

# Amplitud normalizada
amplitude = 2 * np.abs(fft_values) / N

# Corregir componente DC y Nyquist
amplitude[0] /= 2

if N % 2 == 0:
    amplitude[-1] /= 2

# ==========================================
# GRAFICAR FFT
# ==========================================

plt.figure(figsize=(14, 6))

plt.plot(
    frequencies,
    amplitude,
    color='blue',
    linewidth=0.8
)

plt.title("FFT - Raw Data", fontsize=20)
plt.xlabel("Frecuencia (Hz)", fontsize=16)
plt.ylabel("Amplitud", fontsize=16)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.grid(True, alpha=0.3)

plt.xlim(0, fs/2)

plt.tight_layout()
plt.show()

# ==========================================
# GRAFICAR FFT por debajo de 100 Hz
# ==========================================

plt.figure(figsize=(14, 6))

plt.plot(
    frequencies,
    amplitude,
    color='blue',
    linewidth=0.8
)

plt.title("FFT - Raw Data", fontsize=20)
plt.xlabel("Frecuencia (Hz)", fontsize=16)
plt.ylabel("Amplitud", fontsize=16)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.grid(True, alpha=0.3)

plt.xlim(0, 100)

plt.tight_layout()
plt.show()


# ==========================================
# 6. GRAFICAR SEÑAL CORTADA CON //
# ==========================================

fig, ax = plt.subplots(figsize=(14, 6))

# Dibujar cada segmento por separado
segments = []

previous_end = None

for start, end in CUT_INTERVALS:

    segment = (
        (cut_time_original < start) |
        (cut_time_original >= end)
    )

# Identificar discontinuidades temporales
breaks = np.where(
    np.diff(cut_time_original) > 1.5 / fs
)[0] + 1

indices = np.split(np.arange(len(cut_time)), breaks)

for idx in indices:
    if len(idx) > 0:
        ax.plot(
            cut_time[idx],
            cut_signal[idx],
            linewidth=0.8,
            color="blue"
        )

# Marcar los cortes con //
for i in range(len(indices) - 1):

    left_idx = indices[i][-1]
    right_idx = indices[i + 1][0]

    x_left = cut_time[left_idx]
    x_right = cut_time[right_idx]

    x_middle = (x_left + x_right) / 2

    ax.axvline(
        x_middle,
        color="red",
        linestyle="--",
        alpha=0.5
    )

    ax.text(
        x_middle,
        0.98,
        "//",
        transform=ax.get_xaxis_transform(),
        fontsize=18,
        fontweight="bold",
        color="red",
        ha="center",
        va="top"
    )

ax.set_title("Señal filtrada y con intervalos eliminados")
ax.set_xlabel("Time (s)",fontsize=20)
ax.set_ylabel("Voltage (V)",fontsize=20)

ax.grid(True)


plt.xticks(fontsize=20)
plt.yticks(fontsize=20)
plt.tight_layout()
plt.show()


# ==========================================
# 7. INFORMACIÓN FINAL
# ==========================================

print("\nPROCESAMIENTO COMPLETADO")

print(f"Duración original: {time[-1]:.2f} s")

print(
    f"Duración eliminada: {removed_duration} s"
)

print(
    f"Duración restante: {cut_time[-1]:.2f} s"
)
