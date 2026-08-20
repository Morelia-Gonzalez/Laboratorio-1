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
   
    # Caso 1: archivo ausente -> valores por defecto, sin excepción
    if not os.path.exists(path):
        return DEFAULT_CONFIG.copy(), (
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
                )
            except Exception:
                pass
        return DEFAULT_CONFIG.copy(), (
        )

    except PermissionError:
        # Caso 3: falta de permisos de lectura
        return DEFAULT_CONFIG.copy(), (
        )

    except OSError as e:
        # Cualquier otro error de E/S inesperado
        return DEFAULT_CONFIG.copy(), (
            f"Error inesperado al leer la configuración ({e}). "
        )


def save_config(config: dict, path: str = CONFIG_PATH,
                 backup_path: str = BACKUP_PATH, tmp_path: str = TMP_PATH):

    validated = _validate(config)

    try:
        # Paso 1: respaldo de la configuración anterior
        if os.path.exists(path):
            try:
                shutil.copy2(path, backup_path)
            except PermissionError:
                return False, (
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
        )

    except OSError as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
        return False, f"Error inesperado al guardar la configuración: {e}"
