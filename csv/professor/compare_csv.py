import csv
from pathlib import Path


def read_csv(file_path):
    """Lee un archivo CSV y devuelve una lista de diccionarios."""
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def compare_rows(old_row, new_row):
    """Compara dos filas y devuelve una lista de las columnas que cambiaron."""
    changed_columns = []
    for key in old_row.keys():
        if old_row[key] != new_row[key]:
            changed_columns.append(key)
    return changed_columns


def compare_csv_files(old_file, new_file, output_file):
    """Compara dos archivos CSV y guarda filas nuevas o modificadas en un archivo de salida."""
    old_rows = read_csv(old_file)
    new_rows = read_csv(new_file)

    old_dict = {tuple(row.values()): row for row in old_rows}
    new_dict = {tuple(row.values()): row for row in new_rows}

    fieldnames = list(new_rows[0].keys()) + ["changed_columns"]

    with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for new_row in new_rows:
            old_match = next(
                (
                    old_row
                    for old_row in old_rows
                    if old_row["identity_number"] == new_row["identity_number"]
                ),
                None,
            )
            if not old_match:
                new_row["changed_columns"] = "New row"
                writer.writerow(new_row)
            else:
                changed_cols = compare_rows(old_match, new_row)
                if changed_cols:
                    new_row["changed_columns"] = ", ".join(changed_cols)
                    writer.writerow(new_row)

    print(f"--- Cambios guardados en {output_file} ---")


if __name__ == "__main__":
    new_csv_path = Path("csv/professor/professor_february_2025_cleaned.csv")
    old_csv_path = Path("csv/professor/nov/professor_november_2024_cleaned.csv")
    output_csv_path = Path("csv/professor/compare_results.csv")

    compare_csv_files(old_csv_path, new_csv_path, output_csv_path)
