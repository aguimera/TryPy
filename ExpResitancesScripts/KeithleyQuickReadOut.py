import serial
import time
import csv

# Configura tu puerto COM aquí
PORT = 'COM3'       # <-- CAMBIA esto al puerto correcto
BAUDRATE = 9600
DURATION = 60       # Duración total en segundos
INTERVAL = 0.02        # Intervalo de muestreo en segundos
OUTPUT_FILE = 'corriente_vs_tiempo.csv'

# Abre conexión serial
ser = serial.Serial(
    port=PORT,
    baudrate=BAUDRATE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=2
)

# Espera a que el puerto esté listo
time.sleep(2)

# Configura el Keithley 6514 para medición continua
ser.write(b'*RST\n')                         # Reinicia configuración
time.sleep(0.5)
ser.write(b':FUNC "CURR"\n')                # Selecciona medición de corriente
ser.write(b':FORM:ELEM CURR\n')             # Solo devuelve corriente
ser.write(b':TRIG:COUNT INF\n')             # Modo de lectura continua
ser.write(b':INIT\n')


# ⬇️ PRUEBA DE TASA DE MUESTREO REAL
print("\nMedición de tasa de muestreo real (sin INTERVAL)...")
prev_time = time.time()
for i in range(10):  # Haz 10 lecturas de prueba
    ser.write(b':READ?\n')
    response = ser.readline().decode().strip()
    now = time.time()
    print(f"Muestra {i + 1}: {now - prev_time:.4f} s, Valor: {response}")
    prev_time = now

# Abre archivo CSV
with open(OUTPUT_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Tiempo (s)', 'Corriente (A)'])

    print("Grabando datos...")
    t0 = time.time()
    while True:
        t = time.time() - t0
        if t > DURATION:
            break

        ser.write(b':READ?\n')
        response = ser.readline().decode().strip()

        try:
            current = float(response)
            writer.writerow([round(t, 2), current])
            print(f"{t:.2f} s\t{current:.3e} A")
        except ValueError:
            print(f"Error de lectura: {response}")

        time.sleep(INTERVAL)

print("Grabación finalizada.")
ser.close()
