import requests
import socket
import uuid

# Ruta del archivo donde se almacena la clave privada
PRIVATE_KEY_FILE = 'rsa_private.pem'

# Función para obtener la dirección MAC de la interfaz de red
def get_mac_address():
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 12, 2)])
    return mac

# Función para obtener la IP local
def get_ip_address():
    ip = socket.gethostbyname(socket.gethostname())
    return ip

# Función para cargar la clave privada desde el archivo
def load_private_key():
    try:
        with open(PRIVATE_KEY_FILE, 'rb') as f:
            private_key = f.read()
        return private_key.decode('utf-8')
    except FileNotFoundError:
        print("El archivo de clave privada no fue encontrado.")
        return None

# Función principal del agente
def register_agent():
    # Obtener IP y MAC del agente
    ip = get_ip_address()
    mac = get_mac_address()
    
    # Cargar la clave privada desde el archivo
    private_key = load_private_key()
    
    if not private_key:
        print("No se pudo cargar la clave privada. Abortando el registro.")
        return

    # Configurar el URL del servidor
    server_url = 'http://127.0.0.1:5000/register_agent'
    
    # Preparar los datos para el envío al servidor
    data = {
        'ip': ip,
        'mac': mac,
        'private_key': private_key
    }

    # Realizar el POST al servidor
    response = requests.post(server_url, data=data)
    
    # Verificar la respuesta del servidor
    if response.status_code == 200:
        print("Agente registrado con éxito.")
    else:
        print(f"Error al registrar el agente: {response.text}")

if __name__ == "__main__":
    register_agent()
