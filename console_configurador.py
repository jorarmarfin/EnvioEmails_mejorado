import argparse
from config_manager import ConfigManager
import subprocess
from email_sender import EmailSender
import os
from dotenv import load_dotenv
load_dotenv()

CONFIG_FILE = "config.json"
COUNTER_FILE = "contador/contador.txt"
SENDER_SCRIPT = "sender.py"

def load_body_template(path):
    """Carga la plantilla de correo desde un archivo."""
    if not os.path.exists(path):
        print(f'Error: El archivo de plantilla {path} no existe.')
        return None
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()

def send_single_email(email_address, config_manager):
    """Envía un único correo electrónico."""
    try:
        config = config_manager.load_config()
        smtp_settings = config_manager.get_smtp_settings()
    except FileNotFoundError as e:
        print(f"Error de configuración: {e}. Ejecuta el configurador para crear el archivo.")
        return

    if not all(smtp_settings.values()):
        print("Error: La configuración de SMTP no está completa. Revisa tu archivo .env.")
        return

    email_sender = EmailSender(
        smtp_settings['smtp_host'],
        smtp_settings['smtp_port'],
        smtp_settings['smtp_user'],
        smtp_settings['smtp_password'],
        smtp_settings['email_from']
    )

    body_file = config['body_file']
    subject = config['subject']
    body_template = load_body_template(body_file)
    if body_template is None:
        return

    if email_sender.connect():
        personalized_body = body_template.replace('{{names}}', 'Amigo(a)')
        print(f"Enviando correo a: {email_address}")
        if email_sender.send_email(email_address, subject, personalized_body):
            print("Correo enviado exitosamente.")
        else:
            print("Fallo al enviar el correo.")
        email_sender.disconnect()

def main():
    config_manager = ConfigManager(CONFIG_FILE, COUNTER_FILE)

    parser = argparse.ArgumentParser(
        description="Herramienta de configuración y envío de correos masivos.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''
Ejemplos de uso:
  # Configurar y guardar rutas personalizadas para el próximo envío
  python %(prog)s --set-custom --excel ruta/a/tus/emails.xlsx --body ruta/a/tu/plantilla.html --subject "Nuevo Asunto"

  # Activar la configuración por defecto (usará las rutas en config.json)
  python %(prog)s --set-default

  # Iniciar el envío de correos con la configuración previamente guardada
  python %(prog)s --send

  # Enviar un único correo de prueba a una dirección específica
  python %(prog)s --send-single test@example.com

  # Reiniciar el contador de envíos
  python %(prog)s --reset-counter
'''
    )
    parser.add_argument("--set-default", action="store_true", help="Usar configuración por defecto (definida en config.json)")
    parser.add_argument("--set-custom", action="store_true", help="Usar configuración personalizada (ignora la opción por defecto)")
    parser.add_argument("--excel", type=str, help="Ruta al archivo Excel con los correos.")
    parser.add_argument("--body", type=str, help="Ruta al archivo HTML del cuerpo del correo.")
    parser.add_argument("--subject", type=str, help="Asunto del correo.")
    parser.add_argument("--delay", type=int, help="Retraso en segundos entre cada envío de correo.")
    parser.add_argument("--reset-counter", action="store_true", help="Reiniciar el contador de correos a 0.")
    parser.add_argument("--send", action="store_true", help="Ejecutar el envío de correos con la configuración guardada.")
    parser.add_argument("--send-single", type=str, help="Enviar un único correo a la dirección especificada.")

    args = parser.parse_args()

    if args.send_single:
        send_single_email(args.send_single, config_manager)
        return

    try:
        config = config_manager.load_config()
    except FileNotFoundError:
        print("No se encontró 'config.json'. Creando uno con valores por defecto.")
        config = {}

    if args.set_default:
        config["usar_archivos_por_defecto"] = True
        print("Configurado para usar la configuración por defecto.")
    elif args.set_custom:
        config["usar_archivos_por_defecto"] = False
        print("Configurado para usar la configuración personalizada.")

    if args.excel:
        config["excel_file"] = args.excel
    if args.body:
        config["body_file"] = args.body
    if args.subject:
        config["subject"] = args.subject
    if args.delay:
        config["delay_segundos"] = args.delay

    config_manager.save_config(config)
    print("Configuración guardada en 'config.json'.")

    if args.reset_counter:
        config_manager.reset_counter()
        print("Contador de correos reiniciado a 0.")

    if args.send:
        print("Iniciando el proceso de envío de correos...")
        command = ["python3", SENDER_SCRIPT]
        try:
            subprocess.run(command, check=True)
            print("Proceso de envío finalizado.")
        except subprocess.CalledProcessError as e:
            print(f"El script de envío terminó con un error: {e}")
        except FileNotFoundError:
            print(f"Error: No se encontró el script '{SENDER_SCRIPT}'.")

if __name__ == "__main__":
    main()


