import os
import sys
import json
import subprocess

# Configuración del servidor (ya tenemos la clave por el contexto anterior)
SSH_USER = "root"
SSH_HOST = "vomtu.com"
SSH_PASS = "II+jy8W7RAMtR&0o"
REMOTE_PATH = "/var/www/vomtu"

def run_local(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def run_remote(cmd):
    full_cmd = f"sshpass -p '{SSH_PASS}' ssh -o StrictHostKeyChecking=no {SSH_USER}@{SSH_HOST} \"{cmd}\""
    return subprocess.run(full_cmd, shell=True, capture_output=True, text=True)

def upload_file(local_path, remote_subpath):
    full_remote_path = f"{REMOTE_PATH}/{remote_subpath}"
    cmd = f"sshpass -p '{SSH_PASS}' scp -o StrictHostKeyChecking=no {local_path} {SSH_USER}@{SSH_HOST}:{full_remote_path}"
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def add_testimonial(name, role, text, video_filename, roas):
    file_path = "testimonios.html"
    with open(file_path, "r") as f:
        content = f.read()

    # Preparar el nuevo objeto JS
    new_entry = {
        "name": name,
        "role": role,
        "text": text,
        "videos": [f"roas/{video_filename}"],
        "roas": roas
    }
    
    entry_str = json.dumps(new_entry, ensure_ascii=False)
    
    # Insertar en el array HARDCODED (buscamos el final del array)
    # Buscamos 'const HARDCODED = [' y añadimos después
    marker = "const HARDCODED = ["
    if marker in content:
        parts = content.split(marker)
        updated_content = parts[0] + marker + "\n    " + entry_str + "," + parts[1]
        
        with open(file_path, "w") as f:
            f.write(updated_content)
        print(f"✅ Testimonio de {name} añadido localmente.")
    else:
        print("❌ No se encontró el array HARDCODED en testimonios.html")
        return

def deploy(commit_msg):
    print("🚀 Iniciando despliegue...")
    # 1. Subida a Git
    run_local("git add .")
    run_local(f'git commit -m "{commit_msg}"')
    run_local("git push origin main")
    
    # 2. Pull en servidor
    run_remote(f"cd {REMOTE_PATH} && git pull origin main")
    print("✅ Despliegue completado.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 manage_vomtu.py [add|deploy]")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "add":
        # Ejemplo: python3 manage_vomtu.py add "Nombre" "Rol" "Texto" "video.mp4" "ROAS"
        if len(sys.argv) < 7:
            print("Faltan argumentos para 'add'")
            sys.exit(1)
        add_testimonial(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        
        # Subir el video si existe localmente
        video_path = f"roas/{sys.argv[5]}"
        if os.path.exists(video_path):
            print(f"⬆️ Subiendo vídeo {video_path}...")
            upload_file(video_path, f"roas/{sys.argv[5]}")
            print("✅ Vídeo subido.")
            
    elif action == "deploy":
        msg = sys.argv[2] if len(sys.argv) > 2 else "update from manager"
        deploy(msg)
