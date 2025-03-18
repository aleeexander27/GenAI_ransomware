from flask import Flask, render_template, request, jsonify, send_file, Response
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

def handle_agent_connection(agent_socket, agent_address): # Función para manejar la ejecución de comandos en los agentes
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
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")
    while True:
        agent_socket, agent_address = server_socket.accept()
        threading.Thread(target=handle_agent_connection, args=(agent_socket, agent_address)).start()

if __name__ == '__main__':
    threading.Thread(target=start_socket_server, args=('0.0.0.0', 5001), daemon=True).start()  # Iniciar el servidor de sockets en un hilo separado
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)# Iniciar el servidor Flask