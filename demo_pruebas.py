import json
import os
import stat

import config_manager as cfgm

SEP = "=" * 70


def limpiar():
    for f in (cfgm.CONFIG_PATH, cfgm.BACKUP_PATH, cfgm.TMP_PATH):
        if os.path.exists(f):
            os.chmod(f, stat.S_IWRITE | stat.S_IREAD)
            os.remove(f)


def caso_1_archivo_ausente():
    print(SEP)
    print("CASO 1: archivo de configuración ausente")
    print(SEP)
    limpiar()
    config, msg = cfgm.load_config()
    print("Mensaje al usuario:", msg)
    print("Configuración cargada (por defecto):")
    print(json.dumps(config, ensure_ascii=False, indent=2))


def caso_2_guardado_y_respaldo_con_utf8():
    print(SEP)
    print("CASO 2: guardado normal, respaldo (.bak) y caracteres UTF-8 (tildes/ñ)")
    print(SEP)
    config = cfgm.DEFAULT_CONFIG.copy()
    config["nombre_usuario"] = "José Ñúñez"
    config["idioma"] = "es-ES"
    exito, msg = cfgm.save_config(config)
    print("Guardado 1 exitoso:", exito, "| mensaje:", msg)

    # Segundo guardado: debe generar config.bak con el contenido anterior
    config2 = config.copy()
    config2["nombre_usuario"] = "María José Muñoz"
    config2["tema_interfaz"] = "oscuro"
    exito2, msg2 = cfgm.save_config(config2)
    print("Guardado 2 exitoso:", exito2, "| mensaje:", msg2)

    with open(cfgm.CONFIG_PATH, encoding="utf-8") as f:
        print("\nContenido actual de config.json:")
        print(f.read())

    with open(cfgm.BACKUP_PATH, encoding="utf-8") as f:
        print("Contenido de config.bak (versión anterior respaldada):")
        print(f.read())


def caso_3_archivo_corrupto():
    print(SEP)
    print("CASO 3: archivo corrupto / formato inválido")
    print(SEP)
    # Se corrompe intencionalmente config.json (config.bak sigue siendo válido
    # gracias al caso anterior)
    with open(cfgm.CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write("{ esto no es json valido ,,, ")

    config, msg = cfgm.load_config()
    print("Mensaje al usuario:", msg)
    print("Configuración recuperada (desde config.bak):")
    print(json.dumps(config, ensure_ascii=False, indent=2))


def caso_4_sin_permisos():
    print(SEP)
    print("CASO 4: falta de permisos de escritura")
    print(SEP)
    # Restaurar config.json válido primero
    cfgm.save_config(cfgm.DEFAULT_CONFIG.copy())

    os.chmod(cfgm.CONFIG_PATH, stat.S_IREAD)
    used_chattr = False
    if os.system("chattr +i " + cfgm.CONFIG_PATH + " 2>/dev/null") == 0:
        used_chattr = True

    try:
        exito, msg = cfgm.save_config({"nombre_usuario": "Intento sin permisos"})
        print("Guardado exitoso:", exito)
        print("Mensaje al usuario:", msg)
    finally:
        if used_chattr:
            os.system("chattr -i " + cfgm.CONFIG_PATH + " 2>/dev/null")
        os.chmod(cfgm.CONFIG_PATH, stat.S_IWRITE | stat.S_IREAD)


if __name__ == "__main__":
    caso_1_archivo_ausente()
    caso_2_guardado_y_respaldo_con_utf8()
    caso_3_archivo_corrupto()
    caso_4_sin_permisos()
    print(SEP)
    print("Pruebas finalizadas. Revisa config.json y config.bak generados.")
