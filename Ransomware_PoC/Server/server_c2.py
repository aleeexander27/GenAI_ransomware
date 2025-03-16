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
def handle_agent_connection(agent_socket, agent_address, agent_id):
    print(f"Agente {agent_id} conectado desde {agent_address}")
    connected_agents[agent_id] = agent_socket  # Guardar el socket del agente

    try:
        while True:
            command = agent_socket.recv(1024).decode('utf-8')
            if command.lower() == "exit":
                break
            elif command:
                # Ejecutar el comando y obtener la salida
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                output = result.stdout if result.stdout else result.stderr
                agent_socket.send(output.encode('utf-8'))
            else:
                agent_socket.send("Comando vacío.\n".encode('utf-8'))
    except Exception as e:
        print(f"Error con el agente {agent_id}: {e}")
    finally:
        agent_socket.close()
        connected_agents.pop(agent_id, None)
        print(f"Agente {agent_id} desconectado.")

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    print("Agentes conectados:", connected_agents)  # Depuración
    print("Buscando agente con ID:", agent_id)

    agent_socket = connected_agents.get(agent_id)
    if not agent_socket:
        return jsonify({'error': 'Agente no está conectado'}), 404

    if request.method == 'POST':
        command = request.form.get('command')
        if command:
            try:
                agent_socket.send(command.encode('utf-8'))
                output = agent_socket.recv(1024).decode('utf-8')
                return render_template('execute_commands.html', agent_id=agent_id, command=command, output=output)
            except Exception as e:
                return jsonify({'error': f'Error al comunicarse con el agente: {str(e)}'}), 500
        else:
            return render_template('execute_commands.html', agent_id=agent_id, error='Comando vacío')
    
    return render_template('execute_commands.html', agent_id=agent_id)


# Función para iniciar el servidor de sockets que escuchará las conexiones de los agentes
def start_socket_server(host='0.0.0.0', port=5001):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")

    while True:
        agent_socket, agent_address = server_socket.accept()
        agent_id = len(connected_agents) + 1
        threading.Thread(target=handle_agent_connection, args=(agent_socket, agent_address, agent_id)).start()

if __name__ == '__main__':
    # Iniciar el servidor de sockets en un hilo separado
    threading.Thread(target=start_socket_server, args=('0.0.0.0', 5001), daemon=True).start()
    # Iniciar el servidor Flask
    app.run(debug=True, host="0.0.0.0", port=5000)