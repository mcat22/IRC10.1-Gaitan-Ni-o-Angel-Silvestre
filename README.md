# Proyecto de Automatización con Ansible

Este proyecto usa **Ansible** para automatizar la configuración de servidores en tres entornos: `development`, `staging` y `production`. Utiliza **inventarios separados**, **roles**, y **variables por entorno**.

---

## 📂 Estructura del Proyecto

```
ansible/
├── desafio.yml                # Playbook anterior (puede eliminarse si no se usa)
├── site.yml                   # Playbook principal por roles
├── files/
│   └── index.html             # Archivo web a desplegar
├── inventories/
│   ├── development/
│   │   ├── hosts              # Inventario para desarrollo
│   │   └── group_vars/
│   │       └── all.yml        # Variables para desarrollo
│   ├── staging/
│   │   ├── hosts
│   │   └── group_vars/
│   │       └── all.yml
│   └── production/
│       ├── hosts
│       └── group_vars/
│           └── all.yml
├── roles/
│   └── webserver/
│       ├── tasks/
│       │   └── main.yml       # Tareas para configurar el servidor web (Apache)
│       └── files/
│           └── index.html     # Copia del archivo web
```

---

## 🧾 Paso a paso realizado

### Paso 1: Crear inventarios por entorno

```bash
mkdir -p inventories/{development,staging,production}/group_vars
```

Crear archivos de inventario (`hosts`) para cada entorno. Ejemplo para `development`:

```ini
[webservers]
dev-web-01 ansible_host=192.168.159.140 ansible_user=mcat

[dbservers]
dev-db-01 ansible_host=192.168.159.141 ansible_user=mcat

[all:vars]
env=development
```

### Paso 2: Variables por entorno

Archivo `inventories/development/group_vars/all.yml`:

```yaml
env: development
http_port: 8080
max_clients: 50
```

> Repetir para `staging` y `production` cambiando los valores según corresponda.

### Paso 3: Crear rol `webserver`

```bash
ansible-galaxy init roles/webserver
```

Editar `roles/webserver/tasks/main.yml`:

```yaml
- name: Instalar Apache
  ansible.builtin.yum:
    name: httpd
    state: present

- name: Copiar archivo index.html
  ansible.builtin.copy:
    src: index.html
    dest: /var/www/html/index.html
    owner: apache
    group: apache
    mode: '0644'

- name: Iniciar y habilitar Apache
  ansible.builtin.service:
    name: httpd
    state: started
    enabled: true
```

### Paso 4: Crear `site.yml`

```yaml
- name: Configurar servidores web
  hosts: webservers
  become: true
  roles:
    - webserver
```

---

## ▶️ Ejecutar el Playbook

```bash
ansible-playbook -i inventories/development site.yml --ask-become-pass
```

> Cambiar `development` por `staging` o `production` según el entorno deseado.

---

## 🛠 Solución de errores comunes

### SSH - Permiso denegado (root)
Asegúrate de que `ansible_user` sea un usuario válido con acceso SSH. Evita usar `root` directamente.

```ini
ansible_user=mcat
```

Y que puedas conectarte con:
```bash
ssh mcat@192.168.159.140
```

---

Este archivo resume todo el trabajo realizado hasta el momento. Se puede seguir construyendo sobre esta base, agregando nuevos roles, tareas, y entornos conforme se amplíen las necesidades.
