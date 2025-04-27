# Comandos no llegan agentes

**Created:** 3/17/2025 11:43  

## Prompt:
no están llegando correctamente los comandos al agente: from flask import Flask, render_template, request, jsonify, send_file, Response
from io import BytesIO
import socket, threading, subprocess


app = Flask(__name__)

agents = []
next_id = 1  
connected_agents = {}  # Diccionario para almacenar las conexiones de agentes activas

@app.route('/') # Ruta principal 
def index():
    return render_template('index.html', agents=agents)

@app.route('/register_agent', methods=['POST']) # Registro de agentes 
def register_agent():
    global next_id
    ip = request.form.get('ip')
    mac = request.form.get('mac')
    so = request.form.get('so')
    private_key_file = request.files.get('private_key')

    if not ip or not mac or not private_key_file:
        return jsonify({'error': 'Faltan IP, MAC o clave privada'}), 400

    private_key_content = private_key_file.read()

    agent = {
        'id': next_id,
        'ip': ip,
        'mac': mac,
        'so': so,
        'private_key': private_key_content.decode('utf-8') 
    }

    agents.append(agent)
    next_id += 1

    return jsonify({'message': 'Agente registrado con éxito', 'agent_id': agent['id']}), 200

@app.route('/view_private_key/<int:agent_id>', methods=['GET']) # Visualizar clave privada 
def view_private_key(agent_id):
    agent = next((a for a in agents if a['id'] == agent_id), None)
    
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    return render_template('view_key.html', private_key=agent['private_key'])


@app.route('/download_private_key/<int:agent_id>', methods=['GET']) # Descargar la clave privada 
def download_private_key(agent_id):
    agent = next((a for a in agents if a['id'] == agent_id), None)
    
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    private_key_io = BytesIO(agent['private_key'].encode('utf-8'))
    return send_file(private_key_io, as_attachment=True, download_name="rsa_private.pem", mimetype='application/x-pem-file')

# Función para manejar la ejecución de comandos en los agentes
def handle_agent_connection(agent_socket, agent_address):
    global connected_agents  

    try:
        agent_id = agent_socket.recv(1024).decode('utf-8')  # Recibir el ID del agente
        agent_id = int(agent_id)  # Convertir a entero
        print(f"Agente {agent_id} conectado desde {agent_address}")

        connected_agents[agent_id] = agent_socket  # Guardar el socket del agente

        while True:  
            command = agent_socket.recv(1024).decode('utf-8')
            if command.lower() == "exit":
                break
            elif command:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                agent_socket.send(output.encode('utf-8'))
            else:
                agent_socket.send("Comando vacío.\n".encode('utf-8'))

    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        agent_socket.close()
        connected_agents.pop(agent_id, None)  # Eliminar el agente desconectado
        print(f"Agente {agent_id} desconectado.")

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        print("Enviando comando al agente:", command)
        
        agent_socket = connected_agents.get(agent_id)
        print("Conexiones activas:", connected_agents)
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404

        # Enviar el comando al agente
        agent_socket.send(command.encode('utf-8'))

        # Esperar la salida del comando
        output = agent_socket.recv(4096).decode('utf-8')

        return render_template('execute_commands.html', agent_id=agent_id, output=output)

    return render_template('execute_commands.html', agent_id=agent_id)

# Función para iniciar el servidor de sockets que escuchará las conexiones de los agentes
def start_socket_server(host='0.0.0.0', port=5001):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar el puerto
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")

    while True:
        agent_socket, agent_address = server_socket.accept()
        threading.Thread(target=handle_agent_connection, args=(agent_socket, agent_address)).start()

if __name__ == '__main__':
    # Iniciar el servidor de sockets en un hilo separado
    threading.Thread(target=start_socket_server, args=('0.0.0.0', 5001), daemon=True).start()
    # Iniciar el servidor Flask
    app.run(debug=True, host="0.0.0.0", port=5000)

## Response:
Parece que el problema es que los comandos no están llegando correctamente al agente. Aquí algunas posibles razones y soluciones:

### Posibles Problemas y Soluciones:

#### 1️⃣ **El agente no está enviando su ID correctamente**

*   En `handle_agent_connection()`, el servidor espera recibir el ID del agente al conectarse:
    
    ```python
    agent_id = agent_socket.recv(1024).decode('utf-8')
    agent_id = int(agent_id)
    ```
    
    *   Asegúrate de que el agente realmente está enviando su ID antes de esperar comandos.
        

#### 2️⃣ **El socket del agente no se está almacenando correctamente**

*   En `handle_agent_connection()`, el socket del agente se guarda en `connected_agents`:
    
    ```python
    connected_agents[agent_id] = agent_socket
    ```
    
    *   Verifica que `agent_id` sea único para cada agente y que realmente se está guardando en `connected_agents`.
        

#### 3️⃣ **El agente no está escuchando comandos después de conectarse**

*   En la función `execute_command()`, cuando intentas enviar un comando:
    
    ```python
    agent_socket.send(command.encode('utf-8'))
    ```
    
    *   Si el agente no está escuchando correctamente después de conectarse, no recibirá el comando.
        
    *   Asegúrate de que el agente esté en un bucle continuo recibiendo comandos.
        

#### 4️⃣ **El socket puede estar cerrado o no disponible**

*   Si `connected_agents.get(agent_id)` devuelve `None`, puede ser porque el socket se cerró.
    
*   Prueba imprimir `connected_agents` antes de enviar el comando:
    
    ```python
    print("Conexiones activas:", connected_agents)
    ```
    
    *   Si el agente no aparece en `connected_agents`, podría haber un problema con la conexión o la asignación del socket.
        

#### 5️⃣ **Posible problema con el tamaño del buffer**

*   En `execute_command()`, el servidor espera la respuesta con:
    
    ```python
    output = agent_socket.recv(4096).decode('utf-8')
    ```
    
    *   Si la salida del comando es mayor a 4096 bytes, podrías perder datos.
        
    *   Prueba con un bucle para recibir datos hasta que el socket se cierre o no haya más datos:
        
        ```python
        output = ""
        while True:
            chunk = agent_socket.recv(4096).decode('utf-8')
            if not chunk:
                break
            output += chunk
        ```
        

#### 6️⃣ **El agente puede estar cerrando la conexión antes de enviar la respuesta**

*   Verifica que el agente no esté cerrando el socket después de recibir el comando antes de responder.
    

* * *

### 📌 **Prueba de Depuración**

Antes de ejecutar comandos, prueba con estas líneas para verificar la conexión:

1.  En `execute_command()`:
    
    ```python
    print("Enviando comando al agente:", command)
    print("Conexiones activas:", connected_agents)
    ```
    
    *   Así puedes confirmar si el agente está en `connected_agents`.
        
2.  En `handle_agent_connection()`, imprime el comando recibido:
    
    ```python
    print(f"Comando recibido de {agent_id}: {command}")
    ```
    

Si después de esto sigues teniendo problemas, dime qué sale en los `print()` y te ayudo a encontrar la causa exacta. 🚀

## Prompt:
quiero saber si connected agents está guardando: connected_agents[agent_id] = agent_socket  # Guardar el socket del agente

## Response:
Para verificar si `connected_agents` está almacenando correctamente los sockets de los agentes, puedes agregar algunos `print()` en puntos clave de tu código.

### 🔍 **Prueba de Depuración**

1️⃣ **Imprime `connected_agents` después de agregar un agente**  
En la función `handle_agent_connection()`, justo después de asignar el socket:

```python
connected_agents[agent_id] = agent_socket  # Guardar el socket del agente
print(f"Agente {agent_id} almacenado en connected_agents.")
print("Estado actual de connected_agents:", connected_agents)
```

2️⃣ **Imprime `connected_agents` en `execute_command()`**  
Antes de intentar enviar el comando:

```python
print("Conexiones activas:", connected_agents)
if agent_id not in connected_agents:
    print(f"El agente {agent_id} no está en connected_agents.")
    return jsonify({'error': 'Agente no está conectado'}), 404
```

3️⃣ **Verifica si los agentes se eliminan correctamente**  
En el `finally` de `handle_agent_connection()`, al eliminar un agente desconectado:

```python
connected_agents.pop(agent_id, None)  # Eliminar el agente desconectado
print(f"Agente {agent_id} eliminado de connected_agents.")
print("Estado actual de connected_agents:", connected_agents)
```

### 🚀 **Prueba Práctica**

*   Con estos `print()`, revisa los logs de la terminal cuando un agente se conecta y cuando intentas ejecutar un comando.
    
*   Si ves que `connected_agents` está vacío o el `agent_id` no aparece, es posible que:
    
    *   El agente no esté enviando su ID correctamente.
        
    *   La conexión se cierre antes de registrarlo en `connected_agents`.
        

Prueba esto y dime qué aparece en los logs. 🔥

## Prompt:
connected agents no se guarda correctamente en execute commands: from flask import Flask, render_template, request, jsonify, send_file, Response
from io import BytesIO
import socket, threading, subprocess


app = Flask(__name__)

agents = []
next_id = 1  
connected_agents = {}  # Diccionario para almacenar las conexiones de agentes activas

@app.route('/') # Ruta principal 
def index():
    return render_template('index.html', agents=agents)

@app.route('/register_agent', methods=['POST']) # Registro de agentes 
def register_agent():
    global next_id
    ip = request.form.get('ip')
    mac = request.form.get('mac')
    so = request.form.get('so')
    private_key_file = request.files.get('private_key')

    if not ip or not mac or not private_key_file:
        return jsonify({'error': 'Faltan IP, MAC o clave privada'}), 400

    private_key_content = private_key_file.read()

    agent = {
        'id': next_id,
        'ip': ip,
        'mac': mac,
        'so': so,
        'private_key': private_key_content.decode('utf-8') 
    }

    agents.append(agent)
    next_id += 1

    return jsonify({'message': 'Agente registrado con éxito', 'agent_id': agent['id']}), 200

@app.route('/view_private_key/<int:agent_id>', methods=['GET']) # Visualizar clave privada 
def view_private_key(agent_id):
    agent = next((a for a in agents if a['id'] == agent_id), None)
    
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    return render_template('view_key.html', private_key=agent['private_key'])


@app.route('/download_private_key/<int:agent_id>', methods=['GET']) # Descargar la clave privada 
def download_private_key(agent_id):
    agent = next((a for a in agents if a['id'] == agent_id), None)
    
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    private_key_io = BytesIO(agent['private_key'].encode('utf-8'))
    return send_file(private_key_io, as_attachment=True, download_name="rsa_private.pem", mimetype='application/x-pem-file')

# Función para manejar la ejecución de comandos en los agentes
def handle_agent_connection(agent_socket, agent_address):
    global connected_agents  

    try:
        agent_id = agent_socket.recv(1024).decode('utf-8')  # Recibir el ID del agente
        agent_id = int(agent_id)  # Convertir a entero
        print(f"Agente {agent_id} conectado desde {agent_address}")

        connected_agents[agent_id] = agent_socket  # Guardar el socket del agente
        print("Estado actual de connected_agents:", connected_agents)

        while True:  
            command = agent_socket.recv(1024).decode('utf-8')
            if command.lower() == "exit":
                break
            elif command:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                agent_socket.send(output.encode('utf-8'))
            else:
                agent_socket.send("Comando vacío.\n".encode('utf-8'))

    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        agent_socket.close()
        connected_agents.pop(agent_id, None)  # Eliminar el agente desconectado
        print(f"Agente {agent_id} desconectado.")

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    if request.method == 'POST':
        command = request.form.get('command')
        print("Enviando comando al agente:", command)
        
        agent_socket = connected_agents.get(agent_id)
        print("Conexiones activas:", connected_agents)
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404

        # Enviar el comando al agente
        agent_socket.send(command.encode('utf-8'))

        # Esperar la salida del comando
        output = agent_socket.recv(4096).decode('utf-8')

        return render_template('execute_commands.html', agent_id=agent_id, output=output)

    return render_template('execute_commands.html', agent_id=agent_id)

# Función para iniciar el servidor de sockets que escuchará las conexiones de los agentes
def start_socket_server(host='0.0.0.0', port=5001):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilizar el puerto
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")

    while True:
        agent_socket, agent_address = server_socket.accept()
        threading.Thread(target=handle_agent_connection, args=(agent_socket, agent_address)).start()

if __name__ == '__main__':
    # Iniciar el servidor de sockets en un hilo separado
    threading.Thread(target=start_socket_server, args=('0.0.0.0', 5001), daemon=True).start()
    # Iniciar el servidor Flask
    app.run(debug=True, host="0.0.0.0", port=5000)

## Response:
Si `connected_agents` no está guardando correctamente los sockets de los agentes, aquí hay algunas posibles razones y soluciones:

* * *

🚨 **Posibles Problemas y Soluciones**
--------------------------------------

### 1️⃣ **El agente no está enviando su ID correctamente**

En `handle_agent_connection()`, el servidor espera recibir el ID del agente, pero si el agente no lo envía correctamente o hay un retraso, `connected_agents[agent_id]` nunca se guardará.

✅ **Solución:**  
Antes de convertir el ID en entero, imprime lo que recibe:

```python
raw_id = agent_socket.recv(1024).decode('utf-8').strip()
print(f"ID recibido: {raw_id}")
try:
    agent_id = int(raw_id)
except ValueError:
    print("Error: el ID del agente no es un número válido.")
    agent_socket.close()
    return
```

Si `raw_id` está vacío o incorrecto, el agente nunca se guardará en `connected_agents`.

* * *

### 2️⃣ **La variable `connected_agents` está siendo modificada en múltiples hilos**

El servidor usa `threading` para manejar múltiples agentes. Si varios agentes se conectan al mismo tiempo, puede haber una condición de carrera que impida que `connected_agents` almacene bien los sockets.

✅ **Solución:**  
Usa un `threading.Lock()` para sincronizar el acceso a `connected_agents`:

```python
from threading import Lock

connected_agents = {}
connected_agents_lock = Lock()

def handle_agent_connection(agent_socket, agent_address):
    global connected_agents  

    try:
        agent_id = agent_socket.recv(1024).decode('utf-8').strip()
        agent_id = int(agent_id) 
        print(f"Agente {agent_id} conectado desde {agent_address}")

        with connected_agents_lock:  # Bloquear el acceso
            connected_agents[agent_id] = agent_socket  
            print("Estado actual de connected_agents:", connected_agents)

        while True:  
            command = agent_socket.recv(1024).decode('utf-8')
            if command.lower() == "exit":
                break
            elif command:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                agent_socket.send(output.encode('utf-8'))
            else:
                agent_socket.send("Comando vacío.\n".encode('utf-8'))

    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        with connected_agents_lock:
            connected_agents.pop(agent_id, None)  
            print(f"Agente {agent_id} desconectado. Estado actual: {connected_agents}")
        agent_socket.close()
```

Esto evita que `connected_agents` tenga problemas al actualizarse en múltiples hilos.

* * *

### 3️⃣ **El socket del agente se cierra antes de ejecutar comandos**

Si el agente cierra la conexión después de conectarse, `connected_agents[agent_id]` se eliminará automáticamente y no aparecerá en `execute_command()`.

✅ **Solución:**  
Antes de enviar el comando en `execute_command()`, verifica que el socket siga abierto:

```python
if agent_id not in connected_agents or connected_agents[agent_id]._closed:
    print(f"El agente {agent_id} no está en connected_agents o el socket está cerrado.")
    return jsonify({'error': 'Agente no está conectado'}), 404
```

Si `_closed` es `True`, el agente ya no está disponible.

* * *

### 4️⃣ **El servidor Flask y el servidor de sockets corren en hilos distintos**

Cuando `Flask` arranca en `app.run()`, está en un hilo separado del servidor de sockets. Si `connected_agents` se está actualizando en `handle_agent_connection()` pero no aparece en `execute_command()`, puede ser un problema de visibilidad entre hilos.

✅ **Solución:**  
Usar una variable global no siempre es seguro. Puedes probar con una estructura compartida como `multiprocessing.Manager().dict()`, pero el `threading.Lock()` en la segunda solución es más sencillo.

* * *

### 5️⃣ **`connected_agents` se borra antes de tiempo**

Si el agente se desconecta por un error en `handle_agent_connection()`, el `finally` borra su entrada de `connected_agents`.

✅ **Solución:**  
Agrega un `print()` antes de la desconexión para confirmar que no está cerrándose por error:

```python
print(f"Verificando antes de desconectar: {connected_agents}")
```

Si ves que `connected_agents` se vacía antes de ejecutar comandos, revisa por qué el agente se está desconectando.

* * *

🔥 **Prueba y Debug**
---------------------

Después de aplicar estos cambios, revisa los logs y dime qué ves. 🚀

## Prompt:
en el handle si se recibe connected agentes: Estado actual de connected_agents: {1: <socket.socket fd=1360, family=2, type=1, proto=0, laddr=('127.0.0.1', 5001), raddr=('127.0.0.1', 50016)>}

## Response:
Si en `handle_agent_connection()` `connected_agents` sí se está actualizando correctamente pero en `execute_command()` aparece vacío o sin el agente correspondiente, entonces el problema está en cómo Flask accede a `connected_agents`.

* * *

🚨 **Posibles Razones y Soluciones**
------------------------------------

### 1️⃣ **El agente se desconectó antes de ejecutar el comando**

Si el socket se cierra antes de que se llame a `execute_command()`, su entrada en `connected_agents` desaparecerá.

✅ **Solución:**  
Verifica en `execute_command()` si el socket sigue abierto antes de usarlo:

```python
agent_socket = connected_agents.get(agent_id)
print("Conexiones activas en execute_command:", connected_agents)

if not agent_socket or agent_socket.fileno() == -1:
    print(f"El agente {agent_id} no está en connected_agents o el socket está cerrado.")
    return jsonify({'error': 'Agente no está conectado'}), 404
```

Si `fileno()` devuelve `-1`, significa que el socket ya se cerró.

* * *

### 2️⃣ **Problema de visibilidad entre hilos**

El servidor Flask y el servidor de sockets corren en hilos diferentes. Flask podría estar accediendo a `connected_agents` antes de que se actualice en `handle_agent_connection()`.

✅ **Solución:**  
Usa `threading.Lock()` para evitar condiciones de carrera:

```python
from threading import Lock
connected_agents_lock = Lock()
```

En `handle_agent_connection()`:

```python
with connected_agents_lock:
    connected_agents[agent_id] = agent_socket
print("Estado actual de connected_agents en handle:", connected_agents)
```

En `execute_command()`:

```python
with connected_agents_lock:
    print("Conexiones activas en execute_command:", connected_agents)
    agent_socket = connected_agents.get(agent_id)
```

Si sigue sin aparecer, Flask está accediendo antes de que `handle_agent_connection()` termine de procesar la conexión.

* * *

### 3️⃣ **El socket server y Flask pueden estar en procesos separados**

Si `start_socket_server()` y `Flask` están en procesos distintos en lugar de hilos, no compartirán variables globales.

✅ **Solución:**  
Cambia el `threading.Thread` en `if __name__ == '__main__'` por `multiprocessing.Process` y usa `multiprocessing.Manager()` para compartir `connected_agents`:

```python
from multiprocessing import Manager, Process

if __name__ == '__main__':
    with Manager() as manager:
        connected_agents = manager.dict()  # Ahora es compartido entre procesos
        socket_server = Process(target=start_socket_server, args=('0.0.0.0', 5001))
        socket_server.start()
        app.run(debug=True, host="0.0.0.0", port=5000)
```

Si el problema es que Flask y el socket server están en procesos distintos, esto lo soluciona.

* * *

🔥 **Pruebas para identificar el error**
----------------------------------------

Antes de modificar código, ejecuta este **test en `execute_command()`**:

```python
print("Estado de connected_agents en execute_command():", connected_agents)
if agent_id not in connected_agents:
    print(f"ERROR: Agente {agent_id} no encontrado en execute_command().")
```

Si aparece vacío en Flask pero no en `handle_agent_connection()`, es un problema de acceso entre hilos/procesos.

Haz estas pruebas y dime qué aparece en los logs. 🚀



---
