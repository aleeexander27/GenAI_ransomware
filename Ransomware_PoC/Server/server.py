from flask import Flask, render_template, request, jsonify, send_file, Response
from io import BytesIO
import socket, threading, subprocess
import time 

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

@app.route('/execute_command/<int:agent_id>', methods=['GET', 'POST'])
def execute_command(agent_id):
    output = None
    if request.method == 'POST':
        command = request.form.get('command')
        print(f"Recibiendo comando para el agente {agent_id}: {command}")
        
        # Verificar si el agente está conectado
        if agent_id in connected_agents:
            agent_socket = connected_agents[agent_id]
            
            # Si el comando es 'exit', cerramos la conexión
            if command == 'exit':
                agent_socket.send(command.encode())
                agent_socket.close()
                connected_agents.pop(agent_id, None)  # Eliminar agente de la lista
                output = f"Conexión con el agente {agent_id} cerrada."
            else:
                # Enviar el comando al agente y esperar la respuesta
                agent_socket.send(command.encode())
                response = agent_socket.recv(4096)
                output = response.decode()
        else:
            output = "Agente no conectado."

    return render_template('execute_commands.html', agent_id=agent_id, output=output)

def start_socket_server(host='0.0.0.0', port=5001):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Servidor de sockets escuchando en {host}:{port}...")
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Conexión desde {client_address}")
            try: 
            # Recibir el ID del agente al inicio de la conexión
                agent_id = int(client_socket.recv(1024).decode('utf-8'))
            # Registrar al agente en la lista de agentes conectados
                connected_agents[agent_id] = client_socket
                print(f"Agente {agent_id} conectado.")
            except Exception as e:
                print(f"Error al recibir datos del agente: {e}")
    finally:
        client_socket.close()
        connected_agents.pop(agent_id, None)
        print(f"Agente {agent_id} desconectado.")


if __name__ == '__main__':
    threading.Thread(target=start_socket_server, args=('0.0.0.0', 5001), daemon=True).start()  # Iniciar el servidor de sockets en un hilo separado
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)# Iniciar el servidor Flask