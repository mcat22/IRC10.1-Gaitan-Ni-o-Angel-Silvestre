# 🚀 Proyecto de Automatización con Docker, Ansible, Flask y Kubernetes

Este proyecto proporciona una solución integral para la automatización y orquestación de servidores Linux mediante **Ansible**, visualizada a través de una interfaz web desarrollada con **Flask** y contenida en **Docker**. Además, incluye el despliegue y preparación de nodos para clústeres de **Kubernetes**, todo gestionado por medio de roles, inventarios y buenas prácticas de infraestructura como código (IaC).

---

## 🧱 Tecnologías utilizadas

- 🐳 Docker
- 🐍 Flask
- 📦 Ansible
- ☸️ Kubernetes (kubeadm, kubelet, kubectl)
- 🌐 HTML + Jinja2
- 🐧 Rocky Linux (nodos gestionados)
- Kali Linux (nodo con Docker)

---

## 🖼️ Vista general del sistema

- Login básico a través de la interfaz Flask.
- Ejecución de tareas de Ansible por botón vía CLI (`subprocess`).
- Visualización de logs de ejecución.
- Automatización de configuración para Apache y Kubernetes usando Ansible.
- Soporte para múltiples entornos (`development`, `staging`, `production`).

---

## 📂 Estructura del proyecto

```
.
├── docker-flask-app/
│   ├── app.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── templates/
│   └── static/
│
├── ansible/
│   ├── site.yml
│   ├── playbook-apache.yml
│   ├── playbook-k8s.yml
│   ├── inventories/
│   │   ├── development/
│   │   ├── staging/
│   │   └── production/
│   └── roles/
│       ├── webserver/
│       ├── apache/
│       └── kubernetes/
└── README.md
```

---


---

## 🐍 Aplicación Flask (app.py)

La aplicación Flask proporciona autenticación básica, ejecución de playbooks remotos vía SSH usando Paramiko, y una interfaz visual para seleccionar y ejecutar los playbooks disponibles. También genera y visualiza logs de actividad.

### Características clave:
- Autenticación por usuario y contraseña.
- Listado remoto de archivos `.yml` en un nodo Rocky Linux vía SSH.
- Ejecución remota de playbooks usando `paramiko`.
- Registro de eventos en logs locales (`logs/ansible-ui.log`).
- Vistas protegidas (`/dashboard`, `/logs`) con control de sesión.

> Los datos de conexión y rutas se configuran directamente en `app.py`. Por seguridad en producción, se recomienda usar variables de entorno.

---

## 🐳 docker-compose.yml

```yaml
version: '3.8'

services:
  flask-saludo-app:
    image: flask-saludo-app
    container_name: flask-saludo-app
    ports:
      - "5001:5050"
    restart: unless-stopped
```

Este archivo permite levantar fácilmente el contenedor con Flask utilizando `docker-compose up -d`.

---

## 📦 requirements.txt

```
flask
paramiko
```

Estas dependencias son necesarias para levantar correctamente la app Flask dentro del contenedor Docker.


## ⚙️ Uso de la interfaz web

docker build -t flask-ansible-app .
docker run -d -p 5100:5001 --name ansible-ui flask-ansible-app


Visita: [http://localhost:5100](http://localhost:5100)


![Captura de pantalla 2025-07-04 222801](https://github.com/user-attachments/assets/23b7294d-2bba-4ed4-a2be-a2cd182e6887)



## 🔗 Integración Flask-Ansible

La app Flask ejecuta comandos de Ansible en una máquina remota (Rocky Linux) vía SSH:

```python
subprocess.run(["ansible-playbook", "playbook-web.yml", "-i", "inventories/development/hosts"])
```

Requisitos:

- Flask con acceso SSH a la máquina con Ansible.
- Permisos `sudo` si se requieren.
- Variables configuradas correctamente por entorno.

---

## 🧾 Automatización con Ansible

![image](https://github.com/user-attachments/assets/33ca5101-01e1-4887-a986-8d0ed0295339)

### 📌 Inventarios por entorno

Ejemplo `inventories/development/hosts`:

  ini
[webservers]
dev-web-01 ansible_host=192.168.159.140 ansible_user=mcat

[dbservers]
dev-db-01 ansible_host=192.168.159.141 ansible_user=mcat

[all:vars]
env=development
```

### 📌 Variables por entorno (`group_vars/all.yml`)

```yaml
env: development
http_port: 8080
max_clients: 50
```

---

## 🧱 Roles de Ansible

### `webserver` / `apache`

Instala y habilita Apache con un archivo personalizado:

```yaml
- name: Instalar Apache
  yum:
    name: httpd
    state: present

- name: Copiar index.html
  copy:
    src: index.html
    dest: /var/www/html/index.html
    mode: '0644'

- name: Habilitar servicio
  service:
    name: httpd
    state: started
    enabled: true
```

### `kubernetes`

Prepara nodos con:

- Instalación de Docker.
- kubelet, kubeadm y kubectl.
- Desactivación de swap.
- Configuración de repositorios.

---

## 📜 Playbooks disponibles

### Instalar Apache

```bash
ansible-playbook -i inventories/development/hosts playbook-apache.yml --ask-become-pass
```

### Preparar nodos Kubernetes

```bash
ansible-playbook -i inventories/development/hosts playbook-k8s.yml --ask-become-pass
```

---

## 👤 Acceso

Login simulado en `login.html`. Recomendaciones:

- Usar `Flask-Login` o JWT.
- Configurar autenticación SSH por clave pública.

---

## 📋 Mejoras pendientes

- Conexión en tiempo real a ejecución de Ansible.
- Métricas por nodo en el dashboard.
- Integración completa con Kubernetes (despliegues y monitoreo desde Flask).
- Autenticación segura.

---

## ✍️ Autor

**Ángel Silvestre Gaitán Niño**  
Proyecto final — Automatización con Ansible, Docker, Flask y Kubernetes  
Instituto IRC 9.1

---

## 🛡️ Licencia

MIT License.
