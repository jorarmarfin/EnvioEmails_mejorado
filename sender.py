import pandas as pd
import os
import logging
import time
import re
from config_manager import ConfigManager
from email_sender import EmailSender

# Límite de correos por sesión SMTP (un poco menos del límite real para seguridad)
SESSION_LIMIT = 4900

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_email(email):
    """Valida el formato de un correo electrónico."""
    if not isinstance(email, str):
        return False
    # Expresión regular para validar un correo electrónico
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def load_body_template(path):
    """Carga la plantilla de correo desde un archivo."""
    if not os.path.exists(path):
        logging.error(f'Error: El archivo de plantilla {path} no existe.')
        return None
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def run_sender():
    """
    Función principal para ejecutar el envío de correos masivos de forma eficiente,
    manejando límites de sesión SMTP y validando correos.
    """
    try:
        config_manager = ConfigManager()
        config = config_manager.load_config()
        smtp_settings = config_manager.get_smtp_settings()
    except FileNotFoundError as e:
        logging.error(f"Error de configuración: {e}. Ejecuta el configurador para crear el archivo.")
        return

    if not all(smtp_settings.values()):
        logging.error("Error: La configuración de SMTP no está completa. Revisa tu archivo .env.")
        return

    email_sender = EmailSender(
        smtp_settings['smtp_host'],
        smtp_settings['smtp_port'],
        smtp_settings['smtp_user'],
        smtp_settings['smtp_password'],
        smtp_settings['email_from']
    )

    excel_file = config['excel_file']
    body_file = config['body_file']
    subject = config['subject']
    delay = config.get('delay_segundos', 1)

    body_template = load_body_template(body_file)
    if body_template is None: return

    if not os.path.exists(excel_file):
        logging.error(f'Error: No se encontró el archivo Excel en la ruta: {excel_file}')
        return

    try:
        df = pd.read_excel(excel_file)
        if 'email' not in df.columns:
            logging.error("El archivo Excel debe contener una columna llamada 'email'.")
            return
    except Exception as e:
        logging.error(f'Error al leer el archivo Excel {excel_file}: {e}')
        return

    start_index = config_manager.read_counter()
    total_emails_in_file = len(df)

    if start_index >= total_emails_in_file:
        logging.info('No hay más correos por enviar. Todos en la lista ya han sido procesados.')
        return

    if not email_sender.connect():
        return

    emails_sent_total = 0
    emails_in_session = 0
    logging.info(f"Iniciando envío desde el correo {start_index + 1} de {total_emails_in_file}.")

    try:
        for index, row in df.iloc[start_index:].iterrows():
            if emails_in_session >= SESSION_LIMIT:
                logging.info(f"Límite de sesión alcanzado ({SESSION_LIMIT} correos). Reiniciando conexión...")
                email_sender.disconnect()
                time.sleep(5)
                if not email_sender.connect():
                    logging.error("No se pudo reconectar al servidor. Abortando el proceso.")
                    break
                emails_in_session = 0

            to_email = row['email']

            if not is_valid_email(to_email):
                logging.warning(f"[{index + 1}/{total_emails_in_file}] Omitiendo correo inválido o nulo en la línea {index + 2}: {to_email}")
                config_manager.save_counter(index + 1) #Avanzo el contador para no reintentar
                continue

            names = row.get('names', 'Amigo(a)')
            personalized_body = body_template.replace('{{names}}', str(names))

            logging.info(f"[{index + 1}/{total_emails_in_file}] Enviando a: {to_email}")

            if email_sender.send_email(to_email, subject, personalized_body):
                config_manager.save_counter(index + 1)
                emails_sent_total += 1
                emails_in_session += 1
            else:
                logging.error(f"Fallo al enviar a {to_email} en la línea {index + 2}. Continuando con el siguiente.")
                config_manager.save_counter(index + 1) #Avanzo el contador para no reintentar

            time.sleep(delay)

    finally:
        email_sender.disconnect()
        logging.info(f"✅ Proceso de envío finalizado. Correos enviados en esta sesión: {emails_sent_total}.")

if __name__ == '__main__':
    run_sender()