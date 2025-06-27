import logging
import os
import re

import pandas as pd
from career_type_mapper import map_career_type

# Configurar el logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Construir la ruta al archivo CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
csv_path = os.path.join(BASE_DIR, "students", "students february 2025.csv")

# Cargar el CSV con pandas
df = pd.read_csv(csv_path, quotechar='"', sep=",", encoding="utf-8")

# Reemplazar NaN con strings vacíos para evitar problemas con valores nulos
df = df.fillna("")

# Convertir todos los valores del DataFrame a cadenas para evitar problemas con tipos de datos
df = df.astype(str)

# Reemplazar los valores "\N" con cadenas vacías
df = df.replace(r"\\N", "", regex=True)

# Reemplazar cualquier otra instancia de "\N" no escapada, por si hay caracteres residuales
df = df.replace(r"\\N", "", regex=True)


# Función para limpiar y validar números de teléfono
def clean_phone_number(phone):
    phone = re.sub(r"\D", "", phone)  # Elimina todo lo que no sea número
    return phone if len(phone) == 10 else ""  # Retorna vacío si no tiene 10 dígitos


# Validar columnas de teléfono
df["phone"] = df["phone"].apply(clean_phone_number)
df["cell_phone"] = df["cell_phone"].apply(clean_phone_number)

df["career_type"] = df["career"].apply(map_career_type)


# Identificar razones de invalidez para cada fila
def identify_invalid_reasons(row):
    reasons = []
    if not row["institutional_email"].endswith("@uvaq.edu.mx"):
        reasons.append("Correo institucional inválido")
    if row["curp"].strip() == "":
        reasons.append("CURP vacío")
    if row["identity_number"].strip() == "":
        reasons.append("Número de identidad vacío")
    if row["cell_phone"] == "":
        reasons.append("Número de celular inválido")
    if row["career_type"].strip() == "unknown":
        reasons.append("Grado actual inválido")
    return ", ".join(reasons)


# Crear la columna con las razones de invalidez
df["reason_invalid"] = df.apply(identify_invalid_reasons, axis=1)

# Filtrar filas inválidas
invalid_rows_df = df[df["reason_invalid"] != ""]

# Guardar las filas inválidas en un nuevo archivo CSV
invalid_rows_path = os.path.join(BASE_DIR, "students", "invalid_rows.csv")
invalid_rows_df.to_csv(invalid_rows_path, index=False, encoding="utf-8")
logger.info(
    f"Se han guardado {len(invalid_rows_df)} registros con datos inválidos en '{invalid_rows_path}'."
)

# Eliminar las filas inválidas del DataFrame original
df = df[df["reason_invalid"] == ""]

# Eliminar la columna de razón de invalidez en el DataFrame limpio
df = df.drop(columns=["reason_invalid"])

# Guardar el archivo original actualizado, sin las filas inválidas
cleaned_csv_path = os.path.join(
    BASE_DIR, "students", "students_november_2024_cleaned.csv"
)
df.to_csv(cleaned_csv_path, index=False, encoding="utf-8")
logger.info(
    f"Se ha actualizado el archivo original sin datos inválidos en '{cleaned_csv_path}'."
)

# Continuar con la lógica original, procesando solo los datos válidos
df["is_duplicate"] = df.duplicated(subset=["photo"], keep=False)
