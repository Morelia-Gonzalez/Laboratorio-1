import os
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog

import config_manager as cfgm


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestor de Configuración de Usuario")
        self.geometry("640x420")

        # --- Carga inicial de configuración ---
        self.config_data, load_msg = cfgm.load_config()
        if load_msg:
            # Aviso no bloqueante al usuario, no una excepción sin control
            self.after(200, lambda: messagebox.showinfo("Configuración", load_msg))

        self._build_menu()
        self._build_body()
        self._apply_config_to_ui()

    # ------------------------------------------------------------------
    # Menú principal
    # ------------------------------------------------------------------
    def _build_menu(self):
        menubar = tk.Menu(self)

        archivo_menu = tk.Menu(menubar, tearoff=0)
        archivo_menu.add_command(label="Nuevo", command=lambda: None)
        archivo_menu.add_command(label="Abrir", command=lambda: None)
        archivo_menu.add_command(label="Guardar", command=lambda: None)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Salir", command=self.destroy)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)

        edicion_menu = tk.Menu(menubar, tearoff=0)
        edicion_menu.add_command(label="Deshacer", command=lambda: None)
        edicion_menu.add_command(label="Rehacer", command=lambda: None)
        edicion_menu.add_command(label="Copiar", command=lambda: None)
        edicion_menu.add_command(label="Pegar", command=lambda: None)
        menubar.add_cascade(label="Edición", menu=edicion_menu)

        ver_menu = tk.Menu(menubar, tearoff=0)
        ver_menu.add_command(label="Zoom +", command=lambda: None)
        ver_menu.add_command(label="Zoom -", command=lambda: None)
        ver_menu.add_command(label="Pantalla completa", command=lambda: None)
        menubar.add_cascade(label="Ver", menu=ver_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Abrir Settings...", command=self.open_settings)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        self.config(menu=menubar)

    def _build_body(self):
        self.body = tk.Frame(self)
        self.body.pack(fill="both", expand=True)

        self.welcome_label = tk.Label(
            self.body, text="", font=("Segoe UI", 14)
        )
        self.welcome_label.pack(pady=20)

        self.profile_label = tk.Label(self.body, text="", fg="gray")
        self.profile_label.pack()

        tk.Button(
            self.body, text="Abrir Settings", command=self.open_settings
        ).pack(pady=10)

    def _apply_config_to_ui(self):
        c = self.config_data
        self.welcome_label.config(
            text=f"Bienvenido/a, {c['nombre_usuario']}",
            fg=c["color_letra"],
        )
        self.body.config(bg=c["color_barra_menu"])
        self.welcome_label.config(bg=c["color_barra_menu"])
        foto = c.get("foto_perfil") or "(sin foto seleccionada)"
        self.profile_label.config(
            text=f"Tema: {c['tema_interfaz']}  |  Idioma: {c['idioma']}  |  "
                 f"Fuente: {c['tamano_fuente']}pt\nFoto de perfil: {foto}",
            bg=c["color_barra_menu"],
        )


