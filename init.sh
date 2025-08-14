#!/bin/bash
# Script de inicialización del proyecto

# Verificar si python3 está disponible
if ! command -v python3 &> /dev/null
then
    echo "Error: python3 no está instalado. Por favor, instálalo para continuar." >&2
    exit 1
fi

# Crear entorno virtual
if [ ! -d ".venv" ]; then
    echo "Creando entorno virtual..."
    python3 -m venv .venv
else
    echo "El entorno virtual .venv ya existe."
fi

# Activar entorno virtual y instalar dependencias
echo "Instalando dependencias desde requirements.txt..."
source .venv/bin/activate
pip install -r requirements.txt

# Crear archivo .env de ejemplo si no existe
if [ ! -f ".env" ]; then
    echo "Creando archivo .env de ejemplo..."
    echo "# Configuración del servidor de correo (SMTP)" > .env
    echo "EMAIL_HOST=smtp.example.com" >> .env
    echo "EMAIL_PORT=587" >> .env
    echo "EMAIL_USER=tu_usuario@example.com" >> .env
    echo "EMAIL_PASSWORD=tu_contraseña_secreta" >> .env
    echo "EMAIL_FROM=tu_remitente@example.com" >> .env
    echo -e "\n\033[1;33mIMPORTANTE: Edita el archivo .env con tus credenciales de correo reales.\033[0m"
else
    echo "El archivo .env ya existe. No se ha modificado."
fi

# Crear .gitignore si no existe
if [ ! -f ".gitignore" ]; then
    echo "Creando archivo .gitignore..."
    echo "# Entorno virtual de Python" > .gitignore
    echo ".venv/" >> .gitignore
    echo "\n# Archivo de variables de entorno" >> .gitignore
    echo ".env" >> .gitignore
    echo "\n# Archivos de caché de Python" >> .gitignore
    echo "__pycache__/" >> .gitignore
    echo "*.pyc" >> .gitignore
else
    echo "El archivo .gitignore ya existe."
fi

echo -e "\n\033[1;32m¡Instalación completada!\033[0m"
echo "Para activar el entorno virtual, ejecuta: source .venv/bin/activate"
