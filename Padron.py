import pandas as pd
import json
import os
import re
from glob import glob

# --- Recordatorio: Instalar esta librería para leer XLSX ---
# pip install openpyxl
# --------------------------------------------------------

# --- Variables de Control de Procesamiento ---
CHECKPOINT_FILE = 'checkpoint.json'
OUTPUT_FILE = 'consolidated_data.json'
BATCH_SIZE = 30 # Número de archivos a procesar antes de guardar el progreso y preguntar.

# -----------------------------------------------
# --- Funciones de Gestión de Checkpoints y Datos ---
# -----------------------------------------------

def load_checkpoint(file_path):
    """Carga la lista de archivos ya procesados."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('processed_files', []))
        except json.JSONDecodeError:
            print(f"Advertencia: El archivo de checkpoint '{file_path}' está corrupto. Iniciando desde cero.")
            return set()
    return set()

def save_checkpoint(file_path, processed_files_set):
    """Guarda la lista de archivos procesados."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({'processed_files': sorted(list(processed_files_set))}, f, indent=4)

def load_consolidated_data(output_file):
    """Carga los datos consolidados existentes o retorna un diccionario vacío."""
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Advertencia: El archivo de salida '{output_file}' está corrupto. Sobrescribiendo.")
            return {}
    return {}

def save_consolidated_data(output_file, all_records):
    """Guarda todos los datos consolidados."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_records, f, ensure_ascii=False, indent=4)

# -----------------------------------------------
# --- Funciones de Transformación de Datos ---
# -----------------------------------------------

def extract_record_data(df, start_row_index, col_id_name, col_phone_dir, source_file):
    """Extrae los datos de una única ficha (izquierda o derecha)."""
    try:
        cedula_raw = df.iloc[start_row_index, col_id_name]
        nombre_raw = df.iloc[start_row_index + 1, col_id_name]
        cedula_str = str(cedula_raw).strip()

        # Validar Cedula
        if pd.isna(cedula_raw) or not re.match(r'\d{3}-\d{7}-\d', cedula_str):
            return None

        telefono_raw = df.iloc[start_row_index + 2, col_phone_dir]
        direccion_raw = df.iloc[start_row_index + 3, col_phone_dir]

        # Limpieza de datos
        nombre = str(nombre_raw).strip()
        telefono = str(telefono_raw).strip()
        telefono = re.sub(r'^(Dir:|Tel:)\s*', '', telefono).strip().replace('Tel:', '').replace('Cel I:', '').strip()
        direccion = str(direccion_raw).strip()
        direccion = re.sub(r'^(Dir:|Tel:)\s*', '', direccion).strip()

        # Origen: Extrae los números iniciales del nombre de archivo.
        # Usa os.path.basename para obtener solo el nombre del archivo, no la ruta completa de la subcarpeta.
        base_name = os.path.basename(source_file)
        origen_match = re.search(r'(\d+)\s*\.xlsx', base_name)
        origen = origen_match.group(1) if origen_match else base_name

        return {
            "cedula": cedula_str,
            "nombre": nombre,
            "telefono": telefono,
            "direccion": direccion,
            "origen": origen
        }
    except IndexError:
        return None
    except Exception:
        return None

def transform_padronelectoral_file(file_path):
    """Procesa un archivo XLSX y extrae todos los registros."""
    records = {}
    try:
        # --- CAMBIO CLAVE: Usar pd.read_excel para archivos XLSX ---
        # sheet_name=0 lee la primera hoja. header=None indica que no hay encabezados.
        df = pd.read_excel(file_path, header=None, sheet_name=0)

        # Índices de columna fijos según el análisis de la tabla:
        COL_ID_NAME_LEFT = 4
        COL_PHONE_DIR_LEFT = 7
        COL_ID_NAME_RIGHT = 26
        COL_PHONE_DIR_RIGHT = 29

        start_row_index = 13 # La primera ficha comienza en la fila de índice 13 (fila 14)
        row_step = 5
        num_rows = len(df)

        for i in range(start_row_index, num_rows, row_step):
            # Registro Izquierdo
            left_record = extract_record_data(df, i, COL_ID_NAME_LEFT, COL_PHONE_DIR_LEFT, file_path)
            if left_record:
                records[left_record['cedula']] = {k: v for k, v in left_record.items() if k != 'cedula'}

            # Registro Derecho
            right_record = extract_record_data(df, i, COL_ID_NAME_RIGHT, COL_PHONE_DIR_RIGHT, file_path)
            if right_record:
                records[right_record['cedula']] = {k: v for k, v in right_record.items() if k != 'cedula'}

    except Exception as e:
        print(f"Error al procesar el archivo {file_path}: {e}")

    return records

# -----------------------------------------------
# --- Función Principal de Procesamiento por Lotes ---
# -----------------------------------------------

def process_batch(directory_path='.', file_pattern='Padron.cvs/*.xlsx'):
    """
    Busca archivos, carga el checkpoint, procesa por lotes, guarda el avance y pregunta.
    """
    # 1. Preparar la lista de archivos a procesar
    all_files = sorted(glob(os.path.join(directory_path, file_pattern)))

    if not all_files:
        print(f"🚨 ¡ERROR! No se encontraron archivos que coincidan con el patrón '{file_pattern}' en '{directory_path}'.")
        print("Verifique el nombre de la subcarpeta ('Padron.cvs') y la extensión ('.xlsx').")
        return

    # 2. Cargar estado de progreso y datos consolidados
    processed_files = load_checkpoint(CHECKPOINT_FILE)
    all_records = load_consolidated_data(OUTPUT_FILE)

    pending_files = [f for f in all_files if os.path.basename(f) not in processed_files]
    total_files = len(all_files)
    processed_count = total_files - len(pending_files)
    
    print("\n" + "=" * 60)
    print(f"--- INICIO DEL PROCESAMIENTO POR LOTES ---")
    print(f"Total de archivos encontrados: {total_files}")
    print(f"Archivos procesados hasta ahora: {processed_count}")
    print(f"Archivos pendientes: {len(pending_files)}")
    print("=" * 60 + "\n")

    files_to_process_in_batch = pending_files[:BATCH_SIZE]
    
    if not files_to_process_in_batch:
        print("¡El procesamiento ha finalizado! No hay archivos pendientes.")
        return

    print(f"-> Procesando lote de {len(files_to_process_in_batch)} archivos...")
    
    current_batch_processed = 0
    for file_path in files_to_process_in_batch:
        file_name = os.path.basename(file_path)
        print(f"   -> {file_name}")

        records_from_file = transform_padronelectoral_file(file_path)
        
        # Actualizar los datos y el checkpoint
        all_records.update(records_from_file)
        processed_files.add(file_name)
        current_batch_processed += 1

    # 3. Guardar avance
    save_consolidated_data(OUTPUT_FILE, all_records)
    save_checkpoint(CHECKPOINT_FILE, processed_files)

    newly_processed_total = processed_count + current_batch_processed
    
    print("\n" + "-" * 60)
    print(f"Lote completado. {current_batch_processed} archivos procesados en este lote.")
    print(f"Avance guardado en '{OUTPUT_FILE}' y '{CHECKPOINT_FILE}'.")
    print(f"Total de archivos procesados: {newly_processed_total} / {total_files}")
    print("-" * 60)

    # 4. Pausa y Opción de Continuar (para uso local)
    if newly_processed_total < total_files:
        print(f"Quedan {total_files - newly_processed_total} archivos pendientes.")
        
        # --- DEBE TENER LA LÍNEA 'should_continue = input(...)' DESCOMENTADA EN SU MÁQUINA ---
        should_continue = input("¿Desea continuar con el siguiente lote (s/n)? ").lower()
        if should_continue == 's':
             process_batch(directory_path, file_pattern) # Llamada recursiva para el siguiente lote
        else:
             print("Proceso detenido por el usuario. Puede reanudar ejecutando el script de nuevo.")
             
    else:
        print("Todos los archivos han sido procesados. ¡Trabajo completado!")


# --- EJECUCIÓN DEL SCRIPT FINAL ---
if __name__ == '__main__':
    # Este patrón busca archivos con extensión .xlsx dentro de la subcarpeta 'Padron.cvs'.
    # Si la carpeta se llama diferente (ej. 'PADRON_CVS'), debe ajustarlo aquí.
    # Reemplace la línea al final de Padron.py con esto:
     process_batch(file_pattern='Padron_Data/*.xlsx')
