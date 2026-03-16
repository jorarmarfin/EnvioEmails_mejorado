import json
import logging
import os
import secrets
import shutil
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import dotenv_values
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
ENV_PATH = BASE_DIR / ".env"
TEMPLATES_DIR = BASE_DIR / "templates"
DATA_DIR = BASE_DIR / "data"
TRASH_DIR = BASE_DIR / "trash"

MANAGED_DIRECTORIES = {
    "templates": TEMPLATES_DIR,
    "data": DATA_DIR,
}
ALLOWED_EXTENSIONS = {
    "templates": {".html", ".htm"},
    "data": {".xlsx", ".xls"},
}

SMTP_ENV_KEYS = {
    "smtp_host": "SMTP_HOST",
    "smtp_port": "SMTP_PORT",
    "smtp_user": "SMTP_USER",
    "smtp_password": "SMTP_PASSWORD",
    "smtp_from": "SMTP_FROM",
}


def _load_boot_env() -> Dict[str, str]:
    if not ENV_PATH.exists():
        return {}
    return {k: (v or "") for k, v in dotenv_values(ENV_PATH, interpolate=False).items()}


_boot_env = _load_boot_env()

app = Flask(__name__, template_folder="webui_templates")
app.secret_key = (
    os.getenv("PANEL_SECRET_KEY")
    or _boot_env.get("PANEL_SECRET_KEY")
    or secrets.token_hex(32)
)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB

if not (os.getenv("PANEL_SECRET_KEY") or _boot_env.get("PANEL_SECRET_KEY")):
    logging.warning(
        "PANEL_SECRET_KEY no configurado; usando clave temporal para sesión. "
        "Configúralo en .env para sesiones persistentes."
    )


def ensure_directories() -> None:
    for folder in MANAGED_DIRECTORIES.values():
        folder.mkdir(parents=True, exist_ok=True)
    TRASH_DIR.mkdir(parents=True, exist_ok=True)


ensure_directories()


def load_config() -> Dict:
    if not CONFIG_PATH.exists():
        return {}
    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(config: Dict) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=4, ensure_ascii=False)


def read_env() -> Dict[str, str]:
    if not ENV_PATH.exists():
        return {}
    return {k: (v or "") for k, v in dotenv_values(ENV_PATH, interpolate=False).items()}


def format_env_value(value: str) -> str:
    if value == "":
        return ""
    needs_quotes = (
        value.strip() != value
        or any(char in value for char in [' ', '#', '"', "'"])
    )
    if not needs_quotes:
        return value
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def update_env_file(updates: Dict[str, str]) -> None:
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text(encoding="utf-8").splitlines()

    output_lines = []
    seen_keys = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            output_lines.append(line)
            continue

        key, _value = line.split("=", 1)
        key = key.strip()
        if key in updates:
            output_lines.append(f"{key}={format_env_value(str(updates[key]))}")
            seen_keys.add(key)
        else:
            output_lines.append(line)

    for key, value in updates.items():
        if key not in seen_keys:
            output_lines.append(f"{key}={format_env_value(str(value))}")

    ENV_PATH.write_text("\n".join(output_lines).rstrip() + "\n", encoding="utf-8")


def get_panel_credentials() -> Tuple[str, str, str]:
    env = read_env()
    username = env.get("PANEL_USERNAME", "").strip()
    password_hash = env.get("PANEL_PASSWORD_HASH", "").strip()
    password_plain = env.get("PANEL_PASSWORD", "")

    # Ignora placeholders comunes para evitar falsos "auth_ready".
    if password_hash.upper().startswith("REEMPLAZAR") or password_hash in {"<hash>", "CHANGE_ME"}:
        password_hash = ""

    # Un hash real de Werkzeug incluye separadores '$' (scrypt/pbkdf2).
    # Si no los tiene, se interpreta como password plano legacy.
    if password_hash and "$" not in password_hash:
        if not password_plain:
            password_plain = password_hash
        password_hash = ""

    return (
        username,
        password_hash,
        password_plain,
    )


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def get_csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["_csrf_token"] = token
    return token


def validate_csrf() -> None:
    token = request.form.get("_csrf_token", "")
    if not token or token != session.get("_csrf_token"):
        abort(400, "CSRF token inválido")


@app.context_processor
def inject_csrf_token():
    return {"csrf_token": get_csrf_token()}


def list_section_files(section: str) -> List[Dict]:
    folder = MANAGED_DIRECTORIES[section]
    files = []

    for path in folder.iterdir():
        if not path.is_file():
            continue
        stat = path.stat()
        files.append(
            {
                "name": path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime),
                "editable": section == "templates" and path.suffix.lower() in {".html", ".htm"},
            }
        )

    files.sort(key=lambda item: item["modified"], reverse=True)
    return files


def get_safe_file_path(section: str, filename: str) -> Path:
    safe_filename = secure_filename(filename)
    if not safe_filename:
        abort(400, "Nombre de archivo inválido")

    path = MANAGED_DIRECTORIES[section] / safe_filename
    if path.parent != MANAGED_DIRECTORIES[section]:
        abort(400, "Ruta inválida")

    return path


def get_duplicate_template_path(source_path: Path) -> Path:
    stem = source_path.stem
    suffix = source_path.suffix

    for index in range(1, 1000):
        candidate = source_path.with_name(f"{stem}_copia{index}{suffix}")
        if not candidate.exists():
            return candidate

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return source_path.with_name(f"{stem}_copia_{timestamp}{suffix}")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    configured_user, configured_hash, configured_plain = get_panel_credentials()
    auth_ready = bool(configured_user and (configured_hash or configured_plain))

    if request.method == "POST":
        validate_csrf()

        if not auth_ready:
            flash(
                "Configura PANEL_USERNAME y PANEL_PASSWORD_HASH (o PANEL_PASSWORD) en .env antes de ingresar.",
                "danger",
            )
            return redirect(url_for("login"))

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user_ok = username == configured_user
        if configured_hash:
            pass_ok = check_password_hash(configured_hash, password)
        else:
            pass_ok = password == configured_plain

        if user_ok and pass_ok:
            session["logged_in"] = True
            session["username"] = username
            flash("Sesión iniciada.", "success")
            return redirect(url_for("dashboard"))

        flash("Credenciales inválidas.", "danger")

    return render_template("login.html", auth_ready=auth_ready)


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    validate_csrf()
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    config = load_config()
    files_summary = {
        section: len([p for p in MANAGED_DIRECTORIES[section].iterdir() if p.is_file()])
        for section in MANAGED_DIRECTORIES
    }
    return render_template(
        "dashboard.html",
        config=config,
        files_summary=files_summary,
        send_command="python3 sender.py",
    )


@app.route("/files/<section>")
@login_required
def files(section: str):
    if section not in MANAGED_DIRECTORIES:
        abort(404)

    return render_template(
        "files.html",
        section=section,
        section_title="Templates HTML" if section == "templates" else "Archivos Excel",
        files=list_section_files(section),
        extensions=", ".join(sorted(ALLOWED_EXTENSIONS[section])),
    )


@app.route("/files/<section>/upload", methods=["POST"])
@login_required
def upload_file(section: str):
    if section not in MANAGED_DIRECTORIES:
        abort(404)
    validate_csrf()

    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        flash("Selecciona un archivo para subir.", "danger")
        return redirect(url_for("files", section=section))

    filename = secure_filename(uploaded_file.filename)
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS[section]:
        flash(f"Extensión no permitida. Permitidas: {', '.join(sorted(ALLOWED_EXTENSIONS[section]))}", "danger")
        return redirect(url_for("files", section=section))

    target_path = MANAGED_DIRECTORIES[section] / filename
    replace = request.form.get("replace") == "on"
    if target_path.exists() and not replace:
        flash(
            f"El archivo {filename} ya existe. Marca 'Reemplazar si existe' para sobrescribirlo.",
            "warning",
        )
        return redirect(url_for("files", section=section))

    uploaded_file.save(target_path)
    flash(f"Archivo {filename} subido correctamente.", "success")
    return redirect(url_for("files", section=section))


@app.route("/files/<section>/delete/<filename>", methods=["POST"])
@login_required
def delete_file(section: str, filename: str):
    if section not in MANAGED_DIRECTORIES:
        abort(404)
    validate_csrf()

    source_path = get_safe_file_path(section, filename)
    if not source_path.exists():
        flash("El archivo ya no existe.", "warning")
        return redirect(url_for("files", section=section))

    trash_section = TRASH_DIR / section
    trash_section.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destination = trash_section / f"{timestamp}_{source_path.name}"
    source_path.replace(destination)

    flash(f"Archivo movido a papelera: {destination.name}", "success")
    return redirect(url_for("files", section=section))


@app.route("/files/<section>/download/<filename>")
@login_required
def download_file(section: str, filename: str):
    if section not in MANAGED_DIRECTORIES:
        abort(404)

    file_path = get_safe_file_path(section, filename)
    if not file_path.exists() or not file_path.is_file():
        abort(404)

    return send_file(file_path, as_attachment=True, download_name=file_path.name)


@app.route("/templates/duplicate/<filename>", methods=["POST"])
@login_required
def duplicate_template(filename: str):
    validate_csrf()

    source_path = get_safe_file_path("templates", filename)
    if source_path.suffix.lower() not in ALLOWED_EXTENSIONS["templates"]:
        abort(400, "Solo se pueden duplicar archivos HTML")
    if not source_path.exists() or not source_path.is_file():
        flash("El template ya no existe.", "warning")
        return redirect(url_for("files", section="templates"))

    destination = get_duplicate_template_path(source_path)
    shutil.copy2(source_path, destination)
    flash(f"Template duplicado: {destination.name}", "success")
    return redirect(url_for("files", section="templates"))


@app.route("/templates/edit/<filename>", methods=["GET", "POST"])
@login_required
def edit_template(filename: str):
    template_path = get_safe_file_path("templates", filename)
    if template_path.suffix.lower() not in ALLOWED_EXTENSIONS["templates"]:
        abort(400, "Solo se pueden editar archivos HTML")

    if not template_path.exists():
        abort(404)

    if request.method == "POST":
        validate_csrf()
        content = request.form.get("content", "")
        template_path.write_text(content, encoding="utf-8")
        flash(f"Template {template_path.name} guardado.", "success")
        return redirect(url_for("edit_template", filename=template_path.name))

    content = template_path.read_text(encoding="utf-8")
    return render_template("edit_template.html", filename=template_path.name, content=content)


@app.route("/templates/view/<filename>")
@login_required
def view_template(filename: str):
    template_path = get_safe_file_path("templates", filename)
    if template_path.suffix.lower() not in ALLOWED_EXTENSIONS["templates"]:
        abort(400, "Solo se pueden visualizar archivos HTML")
    if not template_path.exists() or not template_path.is_file():
        abort(404)

    content = template_path.read_text(encoding="utf-8")
    return render_template("view_template.html", filename=template_path.name, content=content)


@app.route("/config", methods=["GET", "POST"])
@login_required
def config():
    current_config = load_config()

    if request.method == "POST":
        validate_csrf()
        action = request.form.get("action")

        if action == "save_campaign":
            excel_filename = secure_filename(request.form.get("excel_file", ""))
            template_filename = secure_filename(request.form.get("body_file", ""))
            subject = request.form.get("subject", "").strip()

            try:
                delay = max(0, int(request.form.get("delay_segundos", "1")))
            except ValueError:
                flash("El delay debe ser un número entero.", "danger")
                return redirect(url_for("config"))

            if excel_filename:
                current_config["excel_file"] = f"data/{excel_filename}"
            if template_filename:
                current_config["body_file"] = f"templates/{template_filename}"

            current_config["subject"] = subject
            current_config["delay_segundos"] = delay
            save_config(current_config)
            flash("Configuración de campaña guardada en config.json.", "success")

        elif action == "save_smtp":
            env = read_env()
            smtp_updates = {
                SMTP_ENV_KEYS["smtp_host"]: request.form.get("smtp_host", "").strip(),
                SMTP_ENV_KEYS["smtp_port"]: request.form.get("smtp_port", "").strip(),
                SMTP_ENV_KEYS["smtp_user"]: request.form.get("smtp_user", "").strip(),
                SMTP_ENV_KEYS["smtp_from"]: request.form.get("smtp_from", "").strip(),
            }

            new_password = request.form.get("smtp_password", "")
            if new_password:
                smtp_updates[SMTP_ENV_KEYS["smtp_password"]] = new_password
            elif env.get(SMTP_ENV_KEYS["smtp_password"]):
                smtp_updates[SMTP_ENV_KEYS["smtp_password"]] = env.get(SMTP_ENV_KEYS["smtp_password"], "")

            update_env_file(smtp_updates)
            flash("Configuración SMTP guardada en .env.", "success")

        else:
            flash("Acción no reconocida.", "warning")

        return redirect(url_for("config"))

    env_values = read_env()

    data_files = sorted([p.name for p in DATA_DIR.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS["data"]])
    template_files = sorted(
        [p.name for p in TEMPLATES_DIR.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXTENSIONS["templates"]]
    )

    selected_excel = Path(current_config.get("excel_file", "")).name
    selected_template = Path(current_config.get("body_file", "")).name

    smtp_config = {
        "smtp_host": env_values.get("SMTP_HOST", ""),
        "smtp_port": env_values.get("SMTP_PORT", ""),
        "smtp_user": env_values.get("SMTP_USER", ""),
        "smtp_from": env_values.get("SMTP_FROM", ""),
    }

    return render_template(
        "config.html",
        current_config=current_config,
        data_files=data_files,
        template_files=template_files,
        selected_excel=selected_excel,
        selected_template=selected_template,
        smtp_config=smtp_config,
    )


if __name__ == "__main__":
    host = os.getenv("PANEL_HOST") or _boot_env.get("PANEL_HOST") or "127.0.0.1"
    port = int(os.getenv("PANEL_PORT") or _boot_env.get("PANEL_PORT") or "5000")

    app.run(host=host, port=port, debug=False)
