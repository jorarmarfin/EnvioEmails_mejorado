import tkinter as tk
from tkinter import filedialog, messagebox
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from config_manager import ConfigManager
from email_sender import EmailSender
import pandas as pd

CONFIG_FILE = "config.json"
COUNTER_FILE = "contador/contador.txt"

class EmailConfiguratorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Configurador y Tester de Correos")
        master.geometry("600x650") # Adjusted height
        master.resizable(False, False)
        self.config_manager = ConfigManager(CONFIG_FILE, COUNTER_FILE)

        try:
            self.config = self.config_manager.load_config()
        except FileNotFoundError:
            # Si no hay config, se crea uno vacío. Se llenará al guardar.
            self.config = {}

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.master, padding=20)
        frame.pack(fill=BOTH, expand=True)

        # --- SECCIÓN DE CONFIGURACIÓN ---
        config_frame = ttk.Labelframe(frame, text="Configuración de Envío", padding=15)
        config_frame.pack(fill=X, expand=True)

        ttk.Label(config_frame, text="Archivo Excel de Destinatarios:").pack(anchor=W)
        self.excel_entry = ttk.Entry(config_frame, width=70)
        self.excel_entry.insert(0, self.config.get("excel_file", "data/emails_test.xlsx"))
        self.excel_entry.pack(anchor=W)
        ttk.Button(config_frame, text="Seleccionar Excel", command=self.seleccionar_excel, bootstyle="primary-outline", width=20).pack(anchor=W, pady=5)

        ttk.Label(config_frame, text="Plantilla de Correo (HTML):").pack(anchor=W, pady=(10, 0))
        self.body_entry = ttk.Entry(config_frame, width=70)
        self.body_entry.insert(0, self.config.get("body_file", "templates/body.html"))
        self.body_entry.pack(anchor=W)
        ttk.Button(config_frame, text="Seleccionar HTML", command=self.seleccionar_body, bootstyle="primary-outline", width=20).pack(anchor=W, pady=5)

        ttk.Label(config_frame, text="Asunto del Correo:").pack(anchor=W, pady=(10, 0))
        self.subject_entry = ttk.Entry(config_frame, width=70)
        self.subject_entry.insert(0, self.config.get("subject", "Asunto de prueba"))
        self.subject_entry.pack(anchor=W, pady=(0, 10))

        ttk.Button(config_frame, text="Guardar Configuración", command=self.actualizar_config, bootstyle="success", width=25).pack(anchor=CENTER, pady=5)

        # --- SECCIÓN DE PRUEBAS ---
        test_frame = ttk.Labelframe(frame, text="Prueba de Envío Uno a Uno", padding=15)
        test_frame.pack(fill=X, expand=True, pady=20)

        self.test_status_var = tk.StringVar(value="Carga tu configuración y presiona \"Enviar Siguiente...\"")
        ttk.Label(test_frame, textvariable=self.test_status_var, wraplength=550, justify=LEFT).pack(anchor=W, pady=(0, 10))

        button_frame = ttk.Frame(test_frame)
        button_frame.pack(fill=X)
        
        ttk.Button(button_frame, text="Enviar Siguiente Correo de Prueba", command=self.enviar_siguiente_prueba, bootstyle="info").pack(side=LEFT, expand=True, padx=5)
        ttk.Button(button_frame, text="Reiniciar Contador a 0", command=self.reiniciar_contador, bootstyle="warning").pack(side=LEFT, expand=True, padx=5)

    def actualizar_config(self):
        self.config["excel_file"] = self.excel_entry.get()
        self.config["body_file"] = self.body_entry.get()
        self.config["subject"] = self.subject_entry.get()
        self.config.setdefault("delay_segundos", 1) # Asegura que delay exista para el sender
        self.config_manager.save_config(self.config)
        messagebox.showinfo("Configuración Guardada", "¡Listo! La configuración ha sido guardada en config.json.")

    def enviar_siguiente_prueba(self):
        self.actualizar_config() # Guardar siempre la config actual antes de enviar

        try:
            df = pd.read_excel(self.excel_entry.get())
            body_template = self._load_body_template(self.body_entry.get())
            if body_template is None: return
        except FileNotFoundError as e:
            messagebox.showerror("Error de Archivo", f"No se encontró el archivo: {e.filename}")
            return
        except Exception as e:
            messagebox.showerror("Error de Lectura", f"No se pudo leer el archivo Excel o la plantilla: {e}")
            return

        contador = self.config_manager.read_counter()
        if contador >= len(df):
            self.test_status_var.set(f"No hay más correos en la lista. Total: {len(df)}. Reinicia el contador para volver a empezar.")
            return

        fila = df.iloc[contador]
        to_email = fila['email']
        names = fila.get('names', 'Amigo(a)')
        personalized_body = body_template.replace('{{names}}', str(names))

        smtp_settings = self.config_manager.get_smtp_settings()
        required_keys = ["smtp_host", "smtp_port", "smtp_user", "smtp_password"]
        if not all(smtp_settings.get(key) for key in required_keys):
            messagebox.showerror("Error de Configuración", "La configuración de SMTP no está completa. Revisa tu archivo .env.")
            return

        email_sender = EmailSender(**smtp_settings)
        self.test_status_var.set(f"Enviando a {to_email}...")
        self.master.update_idletasks()

        if email_sender.connect():
            if email_sender.send_email(to_email, self.subject_entry.get(), personalized_body):
                self.config_manager.save_counter(contador + 1)
                self.test_status_var.set(f"✅ Éxito. Correo [{contador+1}/{len(df)}] enviado a: {to_email}")
            else:
                self.test_status_var.set(f"❌ Falló el envío a: {to_email}. Revisa la consola para más detalles.")
            email_sender.disconnect()
        else:
            self.test_status_var.set("❌ Falló la conexión al servidor SMTP. Revisa tus credenciales en .env")

    def _load_body_template(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                return file.read()
        messagebox.showerror("Error de Plantilla", f"El archivo de plantilla HTML no se encontró en la ruta:\n{path}")
        return None

    def seleccionar_archivo(self, tipo):
        ext = [("Archivos Excel", "*.xlsx")] if tipo == "excel" else [("Archivos HTML", "*.html")]
        return filedialog.askopenfilename(title="Seleccionar archivo", filetypes=ext)

    def seleccionar_excel(self):
        path = self.seleccionar_archivo("excel")
        if path:
            self.excel_entry.delete(0, tk.END)
            self.excel_entry.insert(0, path)

    def seleccionar_body(self):
        path = self.seleccionar_archivo("html")
        if path:
            self.body_entry.delete(0, tk.END)
            self.body_entry.insert(0, path)

    def reiniciar_contador(self):
        if messagebox.askyesno("Confirmar", "¿Estás seguro de que quieres reiniciar el contador a 0?"):
            self.config_manager.reset_counter()
            self.test_status_var.set("Contador reiniciado a 0. Puedes empezar la prueba desde el primer correo.")

if __name__ == "__main__":
    root = ttk.Window(themename="flatly")
    app = EmailConfiguratorGUI(root)
    root.mainloop()


