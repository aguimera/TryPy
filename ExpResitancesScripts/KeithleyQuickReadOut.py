import serial
import time
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

from serial.serialutil import PARITY_EVEN, STOPBITS_ONE, EIGHTBITS


def read_keithley_6514(sampling_rate, duration_sec, port="COM9", baudrate=9600, parity=PARITY_EVEN, bytesize=EIGHTBITS, stopbits=STOPBITS_ONE, output_image='current_vs_time.png', output_csv='data.csv'):
    # Setup serial connection
    ser = serial.Serial(port=port, baudrate=baudrate, parity=parity, bytesize=bytesize,stopbits=stopbits, timeout=1)
    time.sleep(2)  # Wait for connection to stabilize

    # Initialize Keithley 6514 for current measurement
    ser.write(b'*RST\n')             # Reset
    time.sleep(1)
    ser.write(b':FUNC "CURR"\n')     # Set function to current
    ser.write(b':FORM:ELEM READ\n')  # Set output to return only reading
    ser.flushInput()

    # Timing setup
    interval = 1.0 / sampling_rate
    total_samples = int(duration_sec * sampling_rate)

    print(f"Collecting {total_samples} samples at {sampling_rate} Hz for {duration_sec} seconds...")

    times = []
    currents = []
    start_time = time.time()

    while True:
        current_time = time.time() - start_time
        if current_time > duration_sec:
            break

        ser.write(b':READ?\n')
        line = ser.readline().decode().strip()

        try:
            current = float(line)
        except ValueError:
            current = float('nan')  # in case of bad read

        times.append(current_time)
        currents.append(current)
        print(f"{current_time:.3f}s: {current} A")

        # Control sampling rate
        #time.sleep(max(0, (1.0 / sampling_rate)))

    ser.close()

    # Save data
    df = pd.DataFrame({'Time (s)': times, 'Current (A)': currents})
    df.to_csv(output_csv, index=False)

    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(times, currents, label='Current (A)', color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Current (A)')
    plt.title('Current vs Time')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_image)
    plt.show()

    print(f"\nPlot saved as '{output_image}', data saved as '{output_csv}'.")


# Example usage:
if __name__ == "__main__":
    read_keithley_6514(
        port='COM9',              # Change this to your actual COM port (e.g., 'COM3' on Windows or '/dev/ttyUSB0' on Linux)
        baudrate=9600,            # Keithley 6514 default baudrate
        sampling_rate=500,          # in Hz
        duration_sec=10,          # total duration in seconds
        output_image='current_vs_time.png',
        output_csv='data.csv'
    )
