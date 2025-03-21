from flask import Flask, render_template, request, jsonify, send_file, Response
from io import BytesIO
import socket, threading, subprocess
import queue
import time 

app = Flask(__name__)

agents = []
next_id = 1 
connected_agents = {}  # Diccionario para almacenar las conexiones de agentes activas
result_queue = queue.Queue()
command_queue = queue.Queue()

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
    if not ip or not mac or not so or not private_key_file:
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

def handle_agent_connection(agent_socket, agent_address):
    """Maneja la conexión con el agente y espera comandos desde el servidor."""
    global connected_agents
    try:
        agent_id = agent_socket.recv(4096).decode('utf-8').strip()
        agent_id = int(agent_id)
        print(f"Agente {agent_id} conectado desde {agent_address}")

        connected_agents[agent_id] = agent_socket
        print("Estado actual de connected_agents:", connected_agents)

        while True:
            # Verificar si hay un comando en la cola para enviar al agente
            if not command_queue.empty():
                command = command_queue.get()
                print(f"Enviando comando al agente {agent_id}: {command}")
                agent_socket.send(command.encode('utf-8'))
                # Esperar la respuesta del agente
                output = agent_socket.recv(4096).decode('utf-8')
                print(f"Respuesta del agente {agent_id}: {output}")
                # Si no hay salida, asignamos un mensaje por defecto
                if not output:
                    output = f"Comando {command} ejecutado con éxito (sin salida)."
                # Poner la respuesta en la cola de resultados
                result_queue.put((agent_id, output))

    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        print(f"Agente {agent_id} desconectado, eliminándolo de connected_agents.")
        connected_agents.pop(agent_id, None)
        agent_socket.close()
        print("Estado actual después de la desconexión:", connected_agents)

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    """Enviar comandos desde el servidor al agente y recibir la respuesta."""
    output = None
    if request.method == 'POST':
        command = request.form.get('command')
        print(f"Recibiendo comando para el agente {agent_id}: {command}")
        agent_socket = connected_agents.get(agent_id)
        if not agent_socket:
            return jsonify({'error': 'Agente no está conectado'}), 404
        # Poner el comando en la cola para que el servidor de sockets lo procese
        command_queue.put(command)
        # Esperar hasta que el servidor de sockets ponga el resultado en la cola con un timeout
        timeout = 4  # tiempo de espera en segundos
        start_time = time.time()
        while result_queue.empty() and (time.time() - start_time) < timeout:
            pass  # Esperar hasta que haya un resultado o se alcance el timeout
        # Recuperar la salida del agente de la cola
        if result_queue.empty():
            output = f"Error: El agente {agent_id} no respondió a tiempo."
        else:
            # Recuperar la salida del agente de la cola
            result_agent_id, output = result_queue.get()
            # Asegurarse de que el resultado corresponde al agente correcto
            if result_agent_id != agent_id:
                output = f"Error: El resultado no pertenece al agente {agent_id}."

    return render_template('execute_commands.html', agent_id=agent_id, output=output)

def start_socket_server(host='0.0.0.0', port=5001): # Función para iniciar el servidor de sockets que escuchará las conexiones de los agentes
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")
    while True:
        agent_socket, agent_address = server_socket.accept()
        threading.Thread(target=handle_agent_connection, args=(agent_socket, agent_address)).start()

if __name__ == '__main__':
    threading.Thread(target=start_socket_server, args=('0.0.0.0', 5001), daemon=True).start()  # Iniciar el servidor de sockets en un hilo separado
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)# Iniciar el servidor Flask