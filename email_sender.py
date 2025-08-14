import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

class EmailSender:
    def __init__(self, smtp_host, smtp_port, smtp_user, smtp_password, email_from):
        self.smtp_host = smtp_host
        self.smtp_port = int(smtp_port)
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.email_from = email_from
        self.server = None

    def connect(self):
        """Establece la conexión con el servidor SMTP."""
        try:
            logging.info(f"Conectando al servidor SMTP {self.smtp_host}...")
            self.server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10)
            self.server.starttls()
            self.server.login(self.smtp_user, self.smtp_password)
            logging.info("✅ Conexión SMTP establecida.")
            return True
        except Exception as e:
            logging.error(f"❌ Error al conectar con el servidor SMTP: {e}")
            self.server = None
            return False

    def disconnect(self):
        """Cierra la conexión con el servidor SMTP."""
        if self.server:
            try:
                self.server.quit()
                logging.info("Conexión SMTP cerrada.")
            except Exception as e:
                logging.error(f"Error al cerrar la conexión SMTP: {e}")
            finally:
                self.server = None

    def send_email(self, to_email, subject, body):
        """Envía un correo utilizando la conexión existente."""
        if not self.server:
            logging.error("No hay conexión SMTP activa. No se puede enviar el correo.")
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_from
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))

            self.server.sendmail(self.email_from, to_email, msg.as_string())
            
            # No logueamos aquí para no saturar, el script principal lo hará.
            return True
        except smtplib.SMTPServerDisconnected:
            logging.error("El servidor SMTP se desconectó. Intentando reconectar...")
            # Intentar reconectar una vez
            if self.connect():
                try:
                    self.server.sendmail(self.email_from, to_email, msg.as_string())
                    return True
                except Exception as e:
                    logging.error(f"Error al enviar correo a {to_email} tras reconexión: {e}")
                    return False
            else:
                return False
        except Exception as e:
            logging.error(f"Error al enviar correo a {to_email}: {e}")
            return False


