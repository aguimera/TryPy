import pandas as pd
import os

class ExcelWriter:
    def __init__(self, folderPath, filename, number_of_callbacks):
        self.base_filename = os.path.join(folderPath, filename)
        self.number_of_callbacks = number_of_callbacks
        self.file_index = 0
        self.current_file = self._get_new_filename()
        self.buffer = []  # Acumula los DataFrames antes de guardar
        self.current_size = 0  # Tamaño estimado en memoria

    def _get_new_filename(self):
        return f"{self.base_filename}_{self.file_index}.xlsx"

    def _flush_buffer_to_file(self):
        if not self.buffer:
            return

        self.current_file = self._get_new_filename()

        # Combina todos los DataFrames del buffer en uno solo
        combined_df = pd.concat(self.buffer, ignore_index=True)

        # Guardar el DataFrame combinado en un archivo Excel
        combined_df.to_excel(self.current_file, index=False)
        print(f"Guardado: {self.current_file}")

        # Limpiar el buffer y pasar al siguiente archivo
        self.buffer = []
        self.file_index += 1

    def write(self, df):
        # Añadir el DataFrame al buffer
        self.buffer.append(df)

        # Verificar si el archivo actual excede el tamaño límite
        if len(self.buffer) >= self.number_of_callbacks:
            self._flush_buffer_to_file()

    def close(self):
        # Guardar lo que queda en el buffer en el archivo actual
        self._flush_buffer_to_file()
