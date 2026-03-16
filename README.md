# Envio de Correos Masivos

Proyecto Python para envio de correos masivos desde un Excel (`.xlsx`) usando templates HTML.

## Componentes

- `sender.py`: envio masivo principal.
- `console_configurador.py`: configuracion y pruebas por CLI.
- `gui_configurador.py`: interfaz de escritorio (Tk).
- `panel_web.py`: panel web para gestionar archivos y configuracion (sin envio masivo).
- `api.py`: API de consulta de campañas y contador global.

## Instalacion

1. Ejecuta:
```bash
bash init.sh
```

2. Activa el entorno virtual:
```bash
source .venv/bin/activate
```

3. Instala/actualiza dependencias:
```bash
pip install -r requirements.txt
```

## Configuracion de `.env`

El proyecto usa variables `SMTP_*`:

```dotenv
SMTP_HOST=smtp.tuservidor.com
SMTP_PORT=587
SMTP_USER=tu_correo@dominio.com
SMTP_PASSWORD=tu_clave
SMTP_FROM=tu_remitente@dominio.com
```

Para el panel web (login simple sin DB):

```dotenv
PANEL_USERNAME=admin
PANEL_PASSWORD_HASH=<hash>
# Opcional si no quieres hash: PANEL_PASSWORD=tu_clave_plana
PANEL_SECRET_KEY=<clave_larga_aleatoria>
PANEL_HOST=127.0.0.1
PANEL_PORT=5000
```

Generar hash de password:
```bash
python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('TU_PASSWORD'))"
```

Pega el hash completo en `PANEL_PASSWORD_HASH` y elimina placeholders como `REEMPLAZAR_CON_HASH`.

Generar `PANEL_SECRET_KEY`:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Panel Web

Lanzar panel:
```bash
python3 panel_web.py
```

Funciones del panel:

- Gestion de archivos en `templates/` y `data/`:
  - subir,
  - descargar,
  - reemplazar,
  - eliminar (mueve a `trash/`),
  - duplicar templates,
  - editar HTML de templates,
  - ver vista previa HTML de templates.
- Configuracion de campaña (`config.json`):
  - archivo Excel,
  - template,
  - asunto,
  - delay.
- Configuracion SMTP en `.env`.

El envio masivo final se mantiene por consola.

## Flujo Operativo Recomendado

1. Entra al panel web y prepara:
   - `templates/*.html`
   - `data/*.xlsx`
   - `config.json` y SMTP.

2. Envia un test por consola:
```bash
python3 console_configurador.py --send-single tu_correo@dominio.com
```

3. Si todo esta OK, envia campaña completa:
```bash
python3 sender.py
```

## Login en Apache (recomendado en servidor)

Si publicas el panel en tu servidor, agrega capa extra con Apache Basic Auth.

1. Crea archivo de usuarios:
```bash
htpasswd -cB /etc/apache2/.htpasswd tu_usuario
```

2. Activa modulos necesarios:
```bash
sudo a2enmod proxy proxy_http ssl auth_basic authn_file
```

3. Ejemplo de VirtualHost (HTTPS + proxy + auth):

```apache
<VirtualHost *:443>
    ServerName panel.tudominio.com

    SSLEngine on
    SSLCertificateFile /ruta/fullchain.pem
    SSLCertificateKeyFile /ruta/privkey.pem

    <Location />
        AuthType Basic
        AuthName "Panel Privado"
        AuthUserFile /etc/apache2/.htpasswd
        Require valid-user
    </Location>

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
</VirtualHost>
```

## API de Consulta

Lanzar API:
```bash
python3 -m uvicorn api:app --reload
```

Endpoints:

- `GET /api/campaigns`
- `GET /api/sent/total`

## Estructura Relevante

- `templates/`: templates HTML de correo.
- `data/`: Excel de destinatarios.
- `trash/`: archivos eliminados desde el panel.
- `contador/contador.txt`: progreso de envio.
- `config.json`: campaña activa.
- `.env`: SMTP + credenciales del panel.
