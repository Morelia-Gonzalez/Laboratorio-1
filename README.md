# Gestor de Configuración de Usuario

Aplicación de escritorio (Tkinter) para el Laboratorio No. 1 —
Manejo e implementación de archivos.

## Ejecución

```bash
python app.py
```

Requiere solo la librería estándar de Python (Tkinter viene incluido
en la mayoría de las distribuciones de Python 3).

## Estructura

- `app.py` — Interfaz gráfica: menú principal (Archivo, Edición, Ver
  simulados; Settings funcional) y la ventana de Settings.
- `config_manager.py` — Toda la lógica de persistencia: carga,
  guardado atómico, respaldo (`.bak`) y manejo de errores.
- `demo_pruebas.py` — Script que ejercita, sin GUI, los 4 escenarios
  clave (archivo ausente, guardado + respaldo + UTF-8, archivo
  corrupto, sin permisos) e imprime evidencia para el reporte.
- `evidencia_pruebas.log` — Salida capturada de `demo_pruebas.py`.
- `config.json` / `config.bak` — Ejemplos de archivos de
  configuración generados por la aplicación.

## Formato de almacenamiento: JSON

Se justifica en detalle en el docstring superior de
`config_manager.py` y debe ampliarse en el PDF del laboratorio,
comparándolo contra CSV (alternativa descartada) en términos de
legibilidad, facilidad de parseo, robustez ante corrupción y
extensibilidad.

## Escritura segura y respaldo

`save_config()`:
1. Copia el `config.json` existente a `config.bak` (respaldo de la
   versión anterior) antes de escribir nada nuevo.
2. Escribe el contenido completo a `config.tmp`.
3. Reemplaza `config.json` con `config.tmp` usando `os.replace`
   (operación atómica), evitando archivos a medio escribir si la
   aplicación se cierra abruptamente durante el guardado.

## Manejo de errores

`load_config()` y `save_config()` capturan explícitamente:
- Archivo ausente → valores por defecto, sin excepción.
- Archivo corrupto / JSON inválido → intenta recuperar desde
  `config.bak`; si tampoco es válido, usa valores por defecto.
- Falta de permisos de lectura/escritura → aviso al usuario, sin
  caída de la aplicación.

Todos los casos están cubiertos por pruebas en `demo_pruebas.py`.

## Codificación

Todas las operaciones de E/S usan `encoding="utf-8"` explícito y
`ensure_ascii=False` al serializar, de modo que nombres de usuario
con tildes o ñ (ej. "José Ñúñez") se guarden y recuperen sin
corrupción — ver `config.json` de ejemplo incluido.

## Pendiente para la entrega completa

- Documento PDF con: justificación de formato, fragmentos de código,
  evidencia de los 3 casos de error (puede basarse en
  `evidencia_pruebas.log`), ejemplo de configuración con tildes/ñ, y
  capturas de pantalla de la aplicación en ejecución (requiere
  entorno con GUI para capturarlas).
