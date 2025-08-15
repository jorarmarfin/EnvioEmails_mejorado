# Envio de Correos Masivos

Este es un proyecto de Python para enviar correos masivos utilizando una lista de destinatarios desde un archivo Excel. La aplicación cuenta con dos interfaces: una gráfica (GUI) para uso en estaciones de trabajo y una de línea de comandos (CLI) para uso en servidores.

## Características

- **Envío Eficiente:** Procesa y envía correos en un único proceso para mayor rendimiento.
- **Personalización:** Permite usar plantillas HTML para el cuerpo del correo y personalizarlas con datos del Excel (ej. `{{names}}`).
- **Doble Interfaz:**
    - **GUI (Gráfica):** Una interfaz amigable para configurar y ejecutar los envíos fácilmente.
    - **CLI (Consola):** Permite configurar y lanzar los envíos mediante comandos, ideal para servidores o automatización.
- **Gestión de Progreso:** Guarda el progreso del envío, permitiendo reanudar desde el último correo enviado en caso de interrupción.
- **Configuración Flexible:** Toda la configuración se maneja a través de un archivo `config.json` y las credenciales de forma segura en un archivo `.env`.

## Prerrequisitos

- Python 3.8 o superior.

## Instalación y Configuración

1.  **Ejecutar el script de inicialización:**
    Este script preparará todo lo necesario: creará un entorno virtual, instalará las dependencias y generará los archivos de configuración iniciales.
    ```bash
    bash init.sh
    ```

2.  **Activar el entorno virtual:**
    Cada vez que trabajes en el proyecto en una nueva terminal, activa el entorno:
    ```bash
    source .venv/bin/activate
    ```

3.  **Configurar las credenciales de correo:**
    El script `init.sh` creó un archivo llamado `.env`. **Debes editar este archivo** con tus credenciales reales del servidor de correo (SMTP).
    ```dotenv
    # Archivo: .env
    EMAIL_HOST=smtp.tuservidor.com
    EMAIL_PORT=587
    EMAIL_USER=tu_correo@dominio.com
    EMAIL_PASSWORD=tu_contraseña
    EMAIL_FROM=tu_correo_remitente@dominio.com
    ```

## Formato de Datos (Archivo Excel)

Para que la aplicación funcione correctamente, tu archivo Excel (`.xlsx`) debe tener una columna llamada `email`.

Opcionalmente, puedes añadir otras columnas para personalizar el correo. Por ejemplo, si añades una columna `names`, puedes usar `{{names}}` en tu plantilla HTML, y el sistema la reemplazará con el valor correspondiente de cada fila.

Ejemplo de `data/emails_test.xlsx`:

| email                 | names      |
| --------------------- | ---------- |
| correo1@ejemplo.com   | Juan Pérez |
| correo2@ejemplo.com   | Ana García |

## Cómo Usar la Aplicación

Puedes usar la interfaz gráfica o la de línea de comandos.

### 1. Usando la Interfaz Gráfica (GUI)

Ideal para usar en un PC de escritorio.

-   **Lanzar la aplicación:**
    ```bash
    python3 gui_configurador.py
    ```
-   **Configuración:**
    -   Usa la interfaz para seleccionar tu archivo Excel, tu plantilla HTML y definir el asunto y el retraso entre correos.
    -   Si marcas "Usar configuración por defecto", se usarán los archivos de prueba incluidos en el proyecto.
    -   Guarda tu configuración con el botón "Guardar configuración".
-   **Envío:**
    -   Haz clic en "Ejecutar envío ahora" para iniciar el proceso.
    -   Puedes reiniciar el contador de envíos con "Reiniciar contador a 0".

### 3. Enviar un único correo de prueba

Puedes enviar un correo a un destinatario específico para verificar que la configuración y la plantilla funcionan correctamente.

```bash
python3 console_configurador.py --send-single "correo@ejemplo.com"
```

Esto utilizará la configuración de asunto y cuerpo que esté guardada en `config.json`.