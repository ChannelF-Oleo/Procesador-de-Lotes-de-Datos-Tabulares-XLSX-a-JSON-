import pandas as pd
import json
import os
import re
from glob import glob
import warnings

# Ignorar advertencias de estilos de Excel que no nos interesan
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# ==========================================
# ⚙️ CONFIGURACIÓN INTELIGENTE
# ==========================================
INPUT_FOLDER = 'Padron_Data'   # <--- CAMBIA ESTO si tu carpeta se llama diferente
FILE_PATTERN = '*.xlsx'
CHECKPOINT_FILE = 'checkpoint.json'
OUTPUT_FILE = 'consolidated_data.json'
BATCH_SIZE = 100               # Preguntar cada 100 archivos

# Regex para identificar cédulas (XXX-XXXXXXX-X)
REGEX_CEDULA = r'\b\d{3}-\d{7}-\d\b'

# ==========================================
# 💾 GESTIÓN DE ESTADO (CHECKPOINTS)
# ==========================================

def load_checkpoint(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return set(json.load(f).get('processed_files', []))
        except:
            return set()
    return set()

def save_checkpoint(file_path, processed_files):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump({'processed_files': sorted(list(processed_files))}, f, indent=4)

def load_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_data(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# ==========================================
# 🧠 LÓGICA DE EXTRACCIÓN INTELIGENTE
# ==========================================

def clean_field_data(df, row, col, search_width=6):
    """
    Busca texto en las celdas adyacentes a la derecha.
    Inteligente: Une fragmentos si el texto fue cortado por columnas en Excel.
    """
    if row >= len(df): return ""
    
    # Tomar un slice de la fila, desde la columna actual hasta N columnas a la derecha
    max_col = min(col + search_width, df.shape[1])
    row_values = df.iloc[row, col:max_col].values
    
    text_parts = []
    for val in row_values:
        s_val = str(val).strip()
        if s_val and s_val.lower() != 'nan' and s_val.lower() != 'none':
            text_parts.append(s_val)
            
    full_text = " ".join(text_parts)
    
    # Limpieza final de prefijos comunes basura
    full_text = re.sub(r'^(Tel:|Cel:|Dir:|Cel I:|Cel II:)\s*', '', full_text, flags=re.IGNORECASE)
    full_text = re.sub(r'(Tel:|Cel:|Dir:)', '', full_text, flags=re.IGNORECASE) # Si aparecen en medio
    
    return full_text.strip()

def process_file_smart(file_path):
    """
    Escanea todo el archivo buscando patrones de cédula en cualquier lugar.
    No depende de filas fijas ni estructuras rígidas.
    """
    file_name = os.path.basename(file_path)
    records = {}
    
    try:
        # Leer todo el Excel. header=None es CRUCIAL para no perder la primera fila
        df = pd.read_excel(file_path, header=None, sheet_name=0)
        
        # 1. ESCANEO VECTORIZADO
        # Buscamos en qué columnas aparecen textos que coincidan con el Regex de Cédula
        # Esto es mucho más rápido que iterar celda por celda.
        potential_cols = []
        for col_idx in df.columns:
            # Convertimos a string y buscamos coincidencias
            matches = df[col_idx].astype(str).str.contains(REGEX_CEDULA, na=False, regex=True)
            if matches.any():
                potential_cols.append((col_idx, matches))

        if not potential_cols:
            print(f"   ⚠️  ALERTA: No se encontraron cédulas en {file_name}")
            return {}

        # 2. EXTRACCIÓN RELATIVA
        extracted_count = 0
        
        for col_idx, match_series in potential_cols:
            # Obtenemos los índices de fila donde hay cédulas
            rows_with_ids = match_series[match_series].index.tolist()
            
            for row_idx in rows_with_ids:
                try:
                    # -- A. Cédula --
                    cedula = str(df.iloc[row_idx, col_idx]).strip()
                    
                    # -- B. Nombre (Fila siguiente) --
                    # A veces el nombre está en la misma col, a veces desplazado. 
                    # Usamos clean_field_data con width pequeño para asegurar.
                    nombre = clean_field_data(df, row_idx + 1, col_idx, search_width=2)
                    
                    # -- C. Teléfono (Fila + 2) --
                    telefono = clean_field_data(df, row_idx + 2, col_idx, search_width=5)
                    
                    # -- D. Dirección (Fila + 3) --
                    direccion = clean_field_data(df, row_idx + 3, col_idx, search_width=5)
                    
                    # -- E. Origen (Del nombre de archivo) --
                    origen_match = re.search(r'(\d+)', file_name)
                    origen = origen_match.group(1) if origen_match else file_name

                    # Validación final antes de guardar
                    if re.match(REGEX_CEDULA, cedula):
                        records[cedula] = {
                            "nombre": nombre,
                            "telefono": telefono,
                            "direccion": direccion,
                            "origen": origen
                        }
                        extracted_count += 1
                        
                except Exception as e:
                    # Si falla una fila específica, no detenemos todo el archivo
                    continue

        return records

    except Exception as e:
        print(f"   ❌ ERROR CRÍTICO en {file_name}: {e}")
        return {}

# ==========================================
# 🚀 EJECUCIÓN PRINCIPAL
# ==========================================

def main():
    print("="*60)
    print("   PROCESADOR DE PADRÓN - MODO INTELIGENTE v3.0")
    print("="*60)

    # 1. Preparar lista de archivos
    search_path = os.path.join(INPUT_FOLDER, FILE_PATTERN)
    all_files = sorted(glob(search_path))
    
    if not all_files:
        print(f"🚨 Error: No se encontraron archivos en '{search_path}'")
        return

    # 2. Cargar checkpoints
    processed = load_checkpoint(CHECKPOINT_FILE)
    consolidated_data = load_data(OUTPUT_FILE)
    
    # Filtrar pendientes
    pending = [f for f in all_files if os.path.basename(f) not in processed]
    total_files = len(all_files)
    
    print(f"📁 Archivos Totales: {total_files}")
    print(f"✅ Ya Procesados:    {len(processed)}")
    print(f"⏳ Pendientes:       {len(pending)}")
    print(f"📊 Registros en DB:  {len(consolidated_data)}")
    print("-" * 60)

    if not pending:
        print("¡Todo listo! No hay archivos nuevos para procesar.")
        return

    # 3. Loop de procesamiento
    count_in_batch = 0
    total_new_records = 0
    
    for i, file_path in enumerate(pending):
        file_name = os.path.basename(file_path)
        print(f"[{i+1}/{len(pending)}] Procesando: {file_name} ...", end=" ", flush=True)
        
        # --- LA MAGIA OCURRE AQUÍ ---
        new_records = process_file_smart(file_path)
        # ----------------------------
        
        count_found = len(new_records)
        if count_found > 0:
            print(f"OK ({count_found} regs)")
            consolidated_data.update(new_records)
            total_new_records += count_found
        else:
            print("⚠️ 0 regs") # Se mantiene en la misma linea
            
        processed.add(file_name)
        count_in_batch += 1
        
        # 4. Control de Lotes (Checkpoint)
        if count_in_batch >= BATCH_SIZE:
            print(f"\n💾 Guardando lote de {BATCH_SIZE} archivos...")
            save_data(OUTPUT_FILE, consolidated_data)
            save_checkpoint(CHECKPOINT_FILE, processed)
            print(f"   -> Total actual consolidado: {len(consolidated_data)} registros.")
            
            # Preguntar al usuario
            if i < len(pending) - 1: # Si no es el último
                print("-" * 40)
                user_input = input("¿Continuar con el siguiente lote? (S/N): ").strip().lower()
                if user_input != 's':
                    print("🛑 Proceso detenido por el usuario.")
                    break
                print("-" * 40)
            
            count_in_batch = 0 # Reiniciar contador del lote

    # 5. Guardado final
    print("\n" + "="*60)
    save_data(OUTPUT_FILE, consolidated_data)
    save_checkpoint(CHECKPOINT_FILE, processed)
    
    print("🎉 PROCESO COMPLETADO")
    print(f"Total Registros Finales: {len(consolidated_data)}")
    print("="*60)

if __name__ == '__main__':
    main()
    
    




