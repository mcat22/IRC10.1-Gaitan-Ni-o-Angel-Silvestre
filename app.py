from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import datetime
import paramiko

app = Flask(__name__)
app.secret_key = '6ee7c29b131cb52d9649b6e41c3216c7ddcd21ff78bfa2d1f11bc26053a4bc93'  # Cámbiala en producción

# Usuarios válidos
USERS = {
    'admin': 'admin123',
    'mcat': 'rocky2025'
}

# Archivo de logs
LOG_FILE = 'logs/ansible-ui.log'

# Datos de conexión SSH
SSH_USER = 'gio'
SSH_HOST = '192.168.139.131'
SSH_KEY_PATH = '/root/.ssh/flask-ansible'
REMOTE_PLAYBOOK_PATH = '/home/gio/ansible'

# Función para guardar logs
def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

# Función para listar playbooks remotos (.yml)
def get_playbook_list():
    try:
        key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, pkey=key)

        stdin, stdout, stderr = client.exec_command(f"ls {REMOTE_PLAYBOOK_PATH}/*.yml")
        files = stdout.read().decode().splitlines()
        playbooks = [os.path.basename(f) for f in files]
        client.close()
        return playbooks
    except Exception as e:
        log_event(f"Error al listar playbooks: {str(e)}")
        return []

# Función para ejecutar un playbook por SSH
def ejecutar_playbook_remoto_con_vars(playbook_name, variables):
    try:
        key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, pkey=key)

        # Convertir variables a CLI
        extra_vars = " ".join([f"{k}='{v}'" for k, v in variables.items()])
        command = f"ansible-playbook {REMOTE_PLAYBOOK_PATH}/{playbook_name} --extra-vars \"{extra_vars}\""

        stdin, stdout, stderr = client.exec_command(command)
        salida = stdout.read().decode()
        errores = stderr.read().decode()
        client.close()

        return salida + ("\n--- ERRORES ---\n" + errores if errores else "")
    except Exception as e:
        return f"Error al ejecutar playbook con variables: {str(e)}"

def ejecutar_playbook_remoto(playbook_name):
    try:
        key = paramiko.RSAKey.from_private_key_file(SSH_KEY_PATH)
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(SSH_HOST, username=SSH_USER, pkey=key)

        command = f"ansible-playbook {REMOTE_PLAYBOOK_PATH}/{playbook_name}"
        stdin, stdout, stderr = client.exec_command(command)
        salida = stdout.read().decode()
        errores = stderr.read().decode()
        client.close()

        return salida + ("\n--- ERRORES ---\n" + errores if errores else "")
    except Exception as e:
        return f"Error al ejecutar playbook: {str(e)}"

# Rutas principales
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['username'] = username
            log_event(f"Usuario '{username}' inició sesión")
            return redirect(url_for('dashboard'))
        else:
            flash("Usuario o contraseña incorrectos", 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    user = session.pop('username', None)
    if user:
        log_event(f"Usuario '{user}' cerró sesión")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    playbooks = get_playbook_list()
    output = None

    if request.method == 'POST':
        selected_playbook = request.form.get('playbook')
        if selected_playbook:
            output = ejecutar_playbook_remoto(selected_playbook)
            log_event(f"Usuario '{session['username']}' ejecutó: {selected_playbook}")

    return render_template('dashboard.html', user=session['username'], playbooks=playbooks, output=output)

@app.route('/logs')
def view_logs():
    if 'username' not in session:
        return redirect(url_for('login'))
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            log_content = f.read()
    else:
        log_content = "No hay logs aún."
    return render_template('logs.html', logs=log_content.splitlines())

#se agrega nueva ruta flask
@app.route('/add_ad_user', methods=['GET', 'POST'])
def add_ad_user():
    if 'username' not in session:
        return redirect(url_for('login'))

    mensaje = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']

        # Ejecutar playbook con esos datos
        salida = ejecutar_playbook_remoto_con_vars('crear_usuario_ad.yml', {
            'username': username,
            'password': password,
            'fullname': fullname
        })
        mensaje = f"Resultado:\n{salida}"

    return render_template('add_ad_user.html', user=session['username'], mensaje=mensaje)



# Crear carpeta de logs si no existe
if __name__ == '__main__':
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=5001, debug=True)
