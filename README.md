
# 🧠 Procesador Inteligente del Padrón Electoral (v3.0)

Este proyecto es un **procesador automatizado y tolerante a errores** para consolidar información proveniente de múltiples archivos Excel del padrón electoral.
El sistema identifica **cédulas**, **nombres**, **teléfonos**, **direcciones** y el **origen del archivo**, aun cuando la estructura del documento no sea uniforme.

La idea principal es permitir la lectura masiva de cientos o miles de archivos `.xlsx`, extrayendo datos de manera robusta y guardándolos en un JSON consolidado, usando **checkpoints para no repetir procesamiento**.

---

## 🚀 Características Principales

* 🔍 **Detección automática de cédulas** mediante Regex (formato *XXX-XXXXXXX-X*).
* 🤖 **Extracción inteligente** que reconstruye campos aunque estén fragmentados en varias columnas.
* 📁 **Procesamiento masivo** de archivos Excel.
* 💾 **Checkpoint persistente** para evitar reprocesar archivos ya completados.
* 📊 **Base de datos consolidada** en formato JSON.
* 🛡️ **Tolerante a errores:** si un archivo falla, el proceso continúa sin detenerse.
* ⚡ **Escaneo vectorizado:** identifica columnas relevantes sin recorrer celda por celda.

---

## 📂 Estructura del Proyecto

```
.
├── Padron_Data/              # Carpeta con los .xlsx a procesar
├── consolidated_data.json    # Salida consolidada con todos los registros
├── checkpoint.json           # Archivos ya procesados
├── main.py                   # Script principal (puede tener otro nombre)
└── README.md
```

---

## 🔧 Requisitos

### Python

* Python **3.8+**

### Dependencias

```bash
pip install pandas openpyxl
```

---

## ⚙️ Configuración

Puedes modificar estas constantes dentro del script:

```python
INPUT_FOLDER = 'Padron_Data'
FILE_PATTERN = '*.xlsx'
CHECKPOINT_FILE = 'checkpoint.json'
OUTPUT_FILE = 'consolidated_data.json'
BATCH_SIZE = 100
REGEX_CEDULA = r'\b\d{3}-\d{7}-\d\b'
```

---

## ▶️ Cómo utilizarlo

1. Crea una carpeta llamada `Padron_Data/` y coloca dentro los archivos `.xlsx`.
2. Ejecuta el script:

```bash
python main.py
```

3. El sistema:

   * Leerá todos los archivos.
   * Detectará los no procesados (usando `checkpoint.json`).
   * Extraerá registros válidos.
   * Guardará el progreso automáticamente.
   * Te preguntará cada *BATCH_SIZE* archivos si deseas continuar.

---

## 🧠 ¿Cómo funciona la extracción?

El script utiliza una lógica inteligente en tres pasos:

### 1. Escaneo vectorizado (rápido)

Busca coincidencias con el Regex de cédula **columna por columna**, sin recorrer celda por celda.

### 2. Localización relativa

Una vez detectada una cédula:

* **Nombre** se busca en la siguiente fila.
* **Teléfono** en fila +2.
* **Dirección** en fila +3.
  *(Con tolerancia a columnas desplazadas gracias a `clean_field_data()`.)*

### 3. Limpieza y reconstrucción

El sistema:

* Une texto cortado por columnas.
* Elimina basura como `Tel:`, `Cel:`, `Dir:`.
* Obtiene el origen basado en números del nombre del archivo.

---

## 📤 Salida esperada

El archivo `consolidated_data.json` tendrá una estructura como:

```json
{
    "001-1234567-8": {
        "nombre": "Juan Pérez",
        "telefono": "809-555-1234",
        "direccion": "C/ Duarte #12, Santo Domingo",
        "origen": "050"
    },
    ...
}
```

---

## 🔐 Tolerancia a fallos

* Si un archivo Excel falla → el proceso continúa.
* Si una fila falla → se ignora.
* Si algo ya fue procesado → se salta, gracias a `checkpoint.json`.

---

## 🗂️ Checkpoints

El sistema guarda automáticamente:

### `checkpoint.json`

Lista de archivos ya procesados.

### `consolidated_data.json`

Base de datos acumulada, actualizada en tiempo real.

Esto permite **pausar y reanudar** el procesamiento sin perder progreso.

---

## 🧪 Buenas prácticas recomendadas

* Divide los archivos por lotes si son miles.
* Mantén el JSON final bajo control con versiones periódicas.
* Verifica ocasionalmente que los Excel sigan un formato mínimamente legible.

---

## 🤝 Contribuciones

Pull requests son bienvenidos.
Si deseas proponer mejoras, optimizaciones o nuevas funciones, abre un **Issue**.

---

## 📄 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.




---

# 🧠 Intelligent Electoral Roll Processor (v3.0)

This project is an **automated and fault-tolerant processor** designed to consolidate information from multiple Excel files belonging to an electoral roll dataset.
It identifies **ID numbers**, **names**, **phone numbers**, **addresses**, and **file origin**, even when the structure of the document is inconsistent or irregular.

The main goal is to enable the massive processing of hundreds or thousands of `.xlsx` files, extracting data reliably and saving everything into a consolidated JSON file — with **checkpointing to avoid reprocessing**.

---

## 🚀 Key Features

* 🔍 **Automatic ID detection** via Regex (format *XXX-XXXXXXX-X*).
* 🤖 **Smart extraction engine** that reconstructs fields even when they’re split across multiple Excel columns.
* 📁 **Bulk file processing** for large datasets.
* 💾 **Persistent checkpoint system** to track processed files.
* 📊 **Consolidated JSON output** with all extracted records.
* 🛡️ **Fault-tolerant:** the script never stops due to errors in specific files or rows.
* ⚡ **Vectorized scanning:** identifies relevant columns without iterating cell-by-cell.

---

## 📂 Project Structure

```
.
├── Padron_Data/              # Folder containing all .xlsx files to process
├── consolidated_data.json    # Final consolidated dataset
├── checkpoint.json           # Tracks processed files
├── main.py                   # Main processing script
└── README.md
```

---

## 🔧 Requirements

### Python Version

* Python **3.8+**

### Dependencies

```bash
pip install pandas openpyxl
```

---

## ⚙️ Configuration

You can modify these constants at the top of the script:

```python
INPUT_FOLDER = 'Padron_Data'
FILE_PATTERN = '*.xlsx'
CHECKPOINT_FILE = 'checkpoint.json'
OUTPUT_FILE = 'consolidated_data.json'
BATCH_SIZE = 100
REGEX_CEDULA = r'\b\d{3}-\d{7}-\d\b'
```

---

## ▶️ How to Use

1. Create a folder named `Padron_Data/` and place all `.xlsx` files inside.
2. Run the script:

```bash
python main.py
```

3. The system will:

   * Load all files.
   * Detect unprocessed files using `checkpoint.json`.
   * Extract valid records.
   * Auto-save progress after each batch.
   * Ask whether you want to continue after each batch of `BATCH_SIZE` files.

---

## 🧠 How the Extraction Works

The script uses a robust, three-step extraction logic:

### 1. Vectorized scanning (fast)

Instead of iterating cell-by-cell, the script scans each column for Regex matches of ID numbers.

### 2. Relative field extraction

Once an ID is detected:

* **Name** → next row
* **Phone** → row +2
* **Address** → row +3

*(With tolerance for column shifts thanks to `clean_field_data()`.)*

### 3. Cleaning & Reconstruction

The system:

* Reassembles text split across columns
* Removes garbage such as `Tel:`, `Cel:`, `Dir:`
* Extracts an origin code from the filename

---

## 📤 Expected Output

`consolidated_data.json` will look like:

```json
{
    "001-1234567-8": {
        "nombre": "Juan Pérez",
        "telefono": "809-555-1234",
        "direccion": "C/ Duarte #12, Santo Domingo",
        "origen": "050"
    }
}
```

---

## 🔐 Error Handling

* If a file fails → the process continues.
* If a row fails → it’s skipped.
* If a file is already processed → it’s ignored automatically.

---

## 🗂️ Checkpoint System

The processor maintains two critical files:

### `checkpoint.json`

Tracks processed filenames.

### `consolidated_data.json`

Stores the cumulative dataset.

This enables **pausing and resuming** at any time without losing progress.

---

## 🧪 Recommended Best Practices

* Organize extremely large datasets into batches.
* Create backups of the consolidated JSON periodically.
* Check Excel formatting occasionally to ensure files remain readable.

---

## 🤝 Contributing

Pull requests are welcome.
For suggestions, feature requests, or improvements, feel free to open an **Issue**.

---

## 📄 License

This project is distributed under the **MIT License**.



