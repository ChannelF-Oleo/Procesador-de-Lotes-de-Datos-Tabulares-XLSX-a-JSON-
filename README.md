
# 📂 PADRON\_PY: Procesador de Lotes de Datos Tabulares (XLSX a JSON)



## 📝 Descripción del Proyecto

**PADRON\_PY** es una utilidad de Python diseñada para procesar grandes volúmenes de datos tabulares (como reportes y padrones) distribuidos en múltiples archivos **XLSX**.

El script lee la estructura no estándar de cada archivo, extrae la información relevante (Cédula/ID, Nombre, Teléfono, Dirección), y la consolida en un único documento **JSON**. Utiliza un robusto sistema de **procesamiento por lotes (batch)** y **puntos de control (checkpoint)** que permite detener y reanudar el proceso en cualquier momento sin perder el avance.

-----

## ✨ Características Principales

  * **Consolidación Robusta:** Transforma miles de registros de archivos múltiples (`*.xlsx`) en un JSON centralizado, utilizando el ID/Cédula como clave principal.
  * **Checkpoint y Resiliencia:** Guarda el progreso automáticamente en `checkpoint.json`. Si la ejecución se detiene o falla, el script reanuda desde el último archivo procesado.
  * **Procesamiento por Lotes:** Procesa archivos en lotes de 10 (configurable) y solicita confirmación para continuar, optimizando el uso de memoria RAM.
  * **Trazabilidad:** Agrega la propiedad `origen` a cada registro para rastrear el archivo del cual fue extraído (ej. "0001").

-----

## 🛠️ Instalación y Configuración del Entorno

Para ejecutar este script, necesitarás **Python 3** y las librerías `pandas` y `openpyxl`.

### 1\. Clonar el Repositorio

```bash
git clone https://github.com/TuUsuario/PADRON_PY.git
cd PADRON_PY
```

### 2\. Crear y Activar el Entorno Virtual

Es fundamental trabajar dentro del entorno virtual (`.venv`) para aislar las dependencias:

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar el entorno virtual (en Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activar el entorno virtual (en Linux/macOS)
source .venv/bin/activate
```

### 3\. Instalar Dependencias

Instala las dos librerías necesarias:

```bash
pip install pandas openpyxl
```

-----

## 🚀 Uso y Estructura de Archivos

### 1\. Organización de Archivos

Asegúrate de que el script (`Padron.py`) y tu carpeta de datos estén organizados de esta manera:

```
PADRON_PY/
├── Padron.py
├── .venv/
└── Padron_Data/  <-- La carpeta que contiene todos los archivos XLSX
    ├── 0001.xlsx
    ├── 1215.xlsx
    └── ... (y el resto de sus archivos)
```

> **Nota:** El nombre de la subcarpeta **`Padron_Data`** debe coincidir con el patrón al final de su script. En su caso, si usó **`Padron.cvs`**, debe mantener ese nombre.

### 2\. Ejecutar el Procesamiento

Ejecuta el script principal con el intérprete de tu entorno virtual:

```bash
python Padron.py
```

El script te informará el total de archivos encontrados y comenzará a procesar el primer lote de 10.

### 3\. Interacción y Control

Al finalizar el lote, el script pausará y te preguntará:

```
¿Desea continuar con el siguiente lote (s/n)?
```

  * Escribe **`s`** (sí) para continuar con el siguiente lote.
  * Escribe **`n`** (no) para detener el proceso.

-----

## 💡 Utilidades y Casos de Uso Generalizados

El diseño de procesamiento por lotes con *checkpointing* hace que este script sea una solución robusta para la **consolidación de datos distribuidos** en diversos sectores:

### 1\. Consolidación de Informes Financieros 💰

  * **Situación:** Una organización guarda **reportes de ventas mensuales o balances contables** distribuidos por sucursales o períodos (`Reporte_SucursalA_01.xlsx`).
  * **Utilidad:** El script procesa cada reporte (`.xlsx`), extrae las transacciones, y las consolida en el archivo `consolidated_data.json` para facilitar el análisis global. La propiedad `origen` permite trazar los datos a la sucursal original.

### 2\. Integración de Datos de Múltiples Dispositivos o Sensores (IoT) 📡

  * **Situación:** Tienes una red de dispositivos (ej. medidores, estaciones meteorológicas) que guardan sus lecturas en archivos separados por hora o por ID de dispositivo.
  * **Utilidad:** El script procesa la totalidad de estos archivos por lotes, consolidando las lecturas (temperatura, presión, uso, etc.) en un único *dataset* estructurado.

### 3\. Procesamiento de Resultados de Pruebas Masivas (QA o I+D) 🧪

  * **Situación:** Se ejecutan **pruebas de rendimiento o simulaciones** miles de veces, y cada ejecución genera un archivo de métricas.
  * **Utilidad:** El script unifica rápidamente los resultados de las 400+ ejecuciones, permitiendo al equipo de análisis generar informes comparativos o identificar fallos sin tener que procesar cada archivo individualmente.

### 4\. Flujo de Trabajo con Resiliencia (Funcionalidad Clave) 🛡️

  * **Resiliencia (Falla del Sistema):** Si la ejecución se interrumpe (cierre inesperado o reinicio), el script lee `checkpoint.json` al reanudarse y **continúa automáticamente** desde el último archivo que no pudo terminar. Esto garantiza cero pérdida de progreso.
  * **Control de Recursos:** La configuración de `BATCH_SIZE` evita la sobrecarga de la memoria RAM, permitiendo que el script se ejecute de manera segura en servidores o máquinas con recursos limitados.

-----

## ⚙️ Configuración Avanzada

Puedes modificar estas variables al inicio de `Padron.py` para adaptar el flujo de trabajo:

| Variable | Descripción | Valor Predeterminado |
| :--- | :--- | :--- |
| `BATCH_SIZE` | Número de archivos a procesar antes de pausar y guardar el avance. | `10` |
| `CHECKPOINT_FILE` | Nombre del archivo que almacena la lista de archivos ya procesados. | `'checkpoint.json'` |
| `OUTPUT_FILE` | Nombre del archivo JSON final consolidado. | `'consolidated_data.json'` |
