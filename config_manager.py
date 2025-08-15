import json
import os
from dotenv import load_dotenv

class ConfigManager:
    def __init__(self, config_file="config.json", counter_file="contador/contador.txt"):
        self.config_file = config_file
        self.counter_file = counter_file
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path=dotenv_path)

    def load_config(self):
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"No se encontró {self.config_file}")
        with open(self.config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_config(self, config):
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)

    def get_smtp_settings(self):
        return {
            "smtp_host": os.getenv("SMTP_HOST"),
            "smtp_port": os.getenv("SMTP_PORT"),
            "smtp_user": os.getenv("SMTP_USER"),
            "smtp_password": os.getenv("SMTP_PASSWORD"),
            "email_from": os.getenv("SMTP_FROM")
        }

    def read_counter(self):
        if os.path.exists(self.counter_file):
            with open(self.counter_file, "r") as file:
                return int(file.read().strip())
        return 0

    def save_counter(self, value):
        os.makedirs(os.path.dirname(self.counter_file), exist_ok=True)
        with open(self.counter_file, "w") as file:
            file.write(str(value))

    def reset_counter(self):
        self.save_counter(0)


