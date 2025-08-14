import argparse
from config_manager import ConfigManager
import subprocess

CONFIG_FILE = "config.json"
COUNTER_FILE = "contador/contador.txt"
SENDER_SCRIPT = "sender.py"

def main():
    config_manager = ConfigManager(CONFIG_FILE, COUNTER_FILE)

    parser = argparse.ArgumentParser(description="Herramienta de configuración y envío de correos masivos.")
    parser.add_argument("--set-default", action="store_true", help="Usar configuración por defecto (definida en config.json)")
    parser.add_argument("--set-custom", action="store_true", help="Usar configuración personalizada (ignora la opción por defecto)")
    parser.add_argument("--excel", type=str, help="Ruta al archivo Excel con los correos.")
    parser.add_argument("--body", type=str, help="Ruta al archivo HTML del cuerpo del correo.")
    parser.add_argument("--subject", type=str, help="Asunto del correo.")
    parser.add_argument("--delay", type=int, help="Retraso en segundos entre cada envío de correo.")
    parser.add_argument("--reset-counter", action="store_true", help="Reiniciar el contador de correos a 0.")
    parser.add_argument("--send", action="store_true", help="Ejecutar el envío de correos con la configuración guardada.")

    args = parser.parse_args()

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

if __name__ == "__main__":
    main()


