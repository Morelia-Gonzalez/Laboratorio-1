import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, filedialog

import config_manager as cfgm

if not hasattr(cfgm, "load_config") or not hasattr(cfgm, "save_config"):
    print("=" * 70)
    print("ERROR DE DIAGNÓSTICO: el módulo config_manager importado no tiene")
    print("las funciones esperadas (load_config / save_config).")
    print("Archivo realmente cargado:", getattr(cfgm, "__file__", "desconocido"))
    print("Carpeta de trabajo actual:", os.getcwd())
    print("sys.path[0] (primera carpeta de búsqueda):", sys.path[0])
    print("=" * 70)
    raise SystemExit(
    )


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

    # Menú principal
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

    # Ventana de Settings
    def open_settings(self):
        SettingsWindow(self)

    def on_settings_saved(self, new_config: dict):
        """Callback invocado por SettingsWindow tras un guardado exitoso."""
        self.config_data = new_config
        self._apply_config_to_ui()


class SettingsWindow(tk.Toplevel):
    def __init__(self, parent: App):
        super().__init__(parent)
        self.parent = parent
        self.title("Settings")
        self.geometry("460x420")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        c = parent.config_data
        self.foto_perfil_path = tk.StringVar(value=c.get("foto_perfil", ""))
        self.color_barra_menu = c.get("color_barra_menu", "#2c3e50")
        self.color_letra = c.get("color_letra", "#000000")

        form = tk.Frame(self, padx=16, pady=16)
        form.pack(fill="both", expand=True)

        row = 0

        tk.Label(form, text="Nombre de usuario:").grid(row=row, column=0, sticky="w", pady=6)
        self.nombre_var = tk.StringVar(value=c.get("nombre_usuario", ""))
        tk.Entry(form, textvariable=self.nombre_var, width=28).grid(row=row, column=1, pady=6)
        row += 1

        tk.Label(form, text="Tema de interfaz:").grid(row=row, column=0, sticky="w", pady=6)
        self.tema_var = tk.StringVar(value=c.get("tema_interfaz", "claro"))
        ttk.Combobox(
            form, textvariable=self.tema_var, values=["claro", "oscuro"],
            state="readonly", width=25
        ).grid(row=row, column=1, pady=6)
        row += 1

        tk.Label(form, text="Idioma:").grid(row=row, column=0, sticky="w", pady=6)
        self.idioma_var = tk.StringVar(value=c.get("idioma", "es"))
        ttk.Combobox(
            form, textvariable=self.idioma_var,
            values=["es", "es-ES", "en", "en-US"],
            state="readonly", width=25
        ).grid(row=row, column=1, pady=6)
        row += 1

        tk.Label(form, text="Tamaño de fuente:").grid(row=row, column=0, sticky="w", pady=6)
        self.fuente_var = tk.IntVar(value=c.get("tamano_fuente", 12))
        tk.Spinbox(
            form, from_=8, to=48, textvariable=self.fuente_var, width=26
        ).grid(row=row, column=1, pady=6)
        row += 1

        tk.Label(form, text="Color barra de menú:").grid(row=row, column=0, sticky="w", pady=6)
        self.btn_color_barra = tk.Button(
            form, text=self.color_barra_menu, command=self.pick_color_barra,
            bg=self.color_barra_menu
        )
        self.btn_color_barra.grid(row=row, column=1, sticky="we", pady=6)
        row += 1

        tk.Label(form, text="Color de letra:").grid(row=row, column=0, sticky="w", pady=6)
        self.btn_color_letra = tk.Button(
            form, text=self.color_letra, command=self.pick_color_letra,
            bg=self.color_letra
        )
        self.btn_color_letra.grid(row=row, column=1, sticky="we", pady=6)
        row += 1

        tk.Label(form, text="Foto de perfil:").grid(row=row, column=0, sticky="w", pady=6)
        foto_frame = tk.Frame(form)
        foto_frame.grid(row=row, column=1, sticky="we", pady=6)
        self.foto_label = tk.Label(
            foto_frame, textvariable=self.foto_perfil_path, width=18, anchor="w"
        )
        self.foto_label.pack(side="left")
        tk.Button(foto_frame, text="Elegir...", command=self.pick_photo).pack(side="left")
        row += 1

        btn_frame = tk.Frame(self, pady=12)
        btn_frame.pack()
        tk.Button(btn_frame, text="Guardar", command=self.save, width=12).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancelar", command=self.destroy, width=12).pack(side="left", padx=6)

    def pick_color_barra(self):
        color = colorchooser.askcolor(color=self.color_barra_menu, title="Color de la barra de menú")
        if color and color[1]:
            self.color_barra_menu = color[1]
            self.btn_color_barra.config(text=color[1], bg=color[1])

    def pick_color_letra(self):
        color = colorchooser.askcolor(color=self.color_letra, title="Color de letra")
        if color and color[1]:
            self.color_letra = color[1]
            self.btn_color_letra.config(text=color[1], bg=color[1])

    def pick_photo(self):
        path = filedialog.askopenfilename(
            title="Selecciona una foto de perfil",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"), ("Todos los archivos", "*.*")],
        )
        if path:
            self.foto_perfil_path.set(path)

    def save(self):
        fuente = self.fuente_var.get()
        if fuente < 8 or fuente > 96:
            messagebox.showerror("Valor inválido", "El tamaño de fuente debe estar entre 8 y 96.")
            return

        new_config = {
            "nombre_usuario": self.nombre_var.get().strip() or "Usuario",
            "tema_interfaz": self.tema_var.get(),
            "idioma": self.idioma_var.get(),
            "tamano_fuente": fuente,
            "color_barra_menu": self.color_barra_menu,
            "color_letra": self.color_letra,
            "foto_perfil": self.foto_perfil_path.get(),
        }

        exito, msg = cfgm.save_config(new_config)
        if exito:
            self.parent.on_settings_saved(new_config)
            messagebox.showinfo("Settings", "Configuración guardada correctamente.")
            self.destroy()
        else:
            messagebox.showerror("Error al guardar", msg)


if __name__ == "__main__":
    app = App()
    app.mainloop()
