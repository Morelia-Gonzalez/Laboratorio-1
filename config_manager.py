"""
config_manager.py

Maneja la carga, guardado, respaldo y validación del archivo de
configuración de usuario de la aplicación.

Formato elegido: JSON (UTF-8)
------------------------------
Se eligió JSON sobre otras alternativas (se evaluó especialmente CSV)
por las siguientes razones técnicas:

- Legibilidad: JSON representa de forma natural pares clave-valor y
  tipos anidados (ej. color_barra_menu como string, tamaño_fuente
  como entero), mientras que CSV requeriría columnas fijas y no
  representa bien un objeto de configuración jerárquico.
- Facilidad de parseo: Python trae json en su librería estándar,
  sin dependencias externas, con serialización/deserialización
  segura y tipada. CSV exigiría parseo manual y conversión de tipos.
- Robustez ante corrupción: un JSON corrupto falla de forma
  predecible con json.JSONDecodeError, lo que permite detectar el
  problema y recuperar desde el respaldo. Un CSV corrupto (columna
  faltante, delimitador roto) puede leerse "silenciosamente" con
  datos desalineados sin lanzar una excepción clara.
- Tamaño: para un archivo de configuración pequeño (menos de 1 KB),
  la diferencia de tamaño entre JSON y CSV es irrelevante.
- Extensibilidad: agregar nuevas claves (ej. nuevas preferencias) no
  rompe la estructura, a diferencia de CSV donde agregar una columna
  desalinea las filas existentes si no se regenera todo el archivo.
"""

import json
import os
import shutil
import stat

CONFIG_PATH = "config.json"
BACKUP_PATH = "config.bak"
TMP_PATH = "config.tmp"

DEFAULT_CONFIG = {
    "nombre_usuario": "Usuario",
    "tema_interfaz": "claro",       # claro | oscuro
    "idioma": "es",                  # es | es-ES | en | en-US
    "tamano_fuente": 12,
    "color_barra_menu": "#2c3e50",
    "color_letra": "#000000",
    "foto_perfil": "",
}

REQUIRED_KEYS = set(DEFAULT_CONFIG.keys())


class ConfigError(Exception):
    """Error controlado relacionado con la configuración."""
    pass


def _validate(data: dict) -> dict:
    """Asegura que el dict tenga todas las claves esperadas.
    Si faltan claves (ej. config antigua o parcialmente corrupta),
    se completan con los valores por defecto en lugar de fallar.
    """
    if not isinstance(data, dict):
        raise ConfigError("El contenido del archivo no es un objeto JSON válido.")
    result = DEFAULT_CONFIG.copy()
    for key in REQUIRED_KEYS:
        if key in data:
            result[key] = data[key]
    return result


def load_config(path: str = CONFIG_PATH, backup_path: str = BACKUP_PATH):
    """Carga la configuración desde disco.

    Devuelve una tupla (config: dict, mensaje: str | None).
    El mensaje, cuando no es None, describe una condición no fatal
    que el usuario debería conocer (archivo ausente, corrupto, etc.)

    Nunca lanza una excepción no controlada: cualquier problema de
    E/S o de formato degrada a los valores por defecto (o al
    respaldo, si existe) y retorna un mensaje explicativo.
    """
    # Caso 1: archivo ausente -> valores por defecto, sin excepción
    if not os.path.exists(path):
        return DEFAULT_CONFIG.copy(), (
            "No se encontró un archivo de configuración previo. "
            "Se usarán los valores por defecto."
        )

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _validate(data), None

    except json.JSONDecodeError:
        # Caso 2: archivo corrupto / formato inválido
        if os.path.exists(backup_path):
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return _validate(data), (
                    "El archivo de configuración estaba corrupto. "
                    "Se restauró automáticamente desde el respaldo (config.bak)."
                )
            except Exception:
                pass
        return DEFAULT_CONFIG.copy(), (
            "El archivo de configuración estaba corrupto y no había un "
            "respaldo válido disponible. Se usarán los valores por defecto."
        )

    except PermissionError:
        # Caso 3: falta de permisos de lectura
        return DEFAULT_CONFIG.copy(), (
            "No se tienen permisos de lectura sobre el archivo de "
            "configuración. Se usarán los valores por defecto para esta sesión."
        )

    except OSError as e:
        # Cualquier otro error de E/S inesperado
        return DEFAULT_CONFIG.copy(), (
            f"Error inesperado al leer la configuración ({e}). "
            "Se usarán los valores por defecto."
        )


def save_config(config: dict, path: str = CONFIG_PATH,
                 backup_path: str = BACKUP_PATH, tmp_path: str = TMP_PATH):
    """Guarda la configuración de forma segura.

    Flujo:
      1. Si existe un config.json previo, se copia a config.bak
         (respaldo de la configuración anterior) ANTES de tocar nada.
      2. Se escribe el nuevo contenido completo a un archivo temporal
         (config.tmp), nunca directamente sobre config.json.
      3. Se reemplaza config.json con config.tmp usando os.replace,
         que en sistemas POSIX y Windows modernos es una operación
         atómica: o el archivo queda completamente reemplazado, o
         queda el original intacto. Nunca un estado intermedio.

    Esto evita que un cierre abrupto durante el guardado deje el
    archivo de configuración corrupto o a medio escribir.

    Devuelve (exito: bool, mensaje: str | None)
    """
    validated = _validate(config)

    try:
        # Paso 1: respaldo de la configuración anterior
        if os.path.exists(path):
            try:
                shutil.copy2(path, backup_path)
            except PermissionError:
                return False, (
                    "No se pudo crear el respaldo (config.bak) por falta de "
                    "permisos. No se guardaron los cambios para proteger la "
                    "configuración existente."
                )

        # Paso 2: escritura a archivo temporal, en UTF-8 explícito
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(validated, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # Paso 3: reemplazo atómico
        os.replace(tmp_path, path)
        return True, None

    except PermissionError:
        # Sin permisos de escritura en el directorio o en el archivo
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return False, (
            "No se tienen permisos de escritura para guardar la "
            "configuración. Los cambios no se guardaron."
        )

    except OSError as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return False, f"Error inesperado al guardar la configuración: {e}"
