from flask import Flask, render_template, request, jsonify, send_file
from io import BytesIO

# Inicialización de Flask
app = Flask(__name__)

# Lista para almacenar los agentes (sin base de datos)
agents = []

# Ruta principal que muestra la tabla con los agentes registrados
@app.route('/')
def index():
    return render_template('index.html', agents=agents)

# Ruta para recibir los datos de los agentes (IP, MAC, y clave privada como archivo)
@app.route('/register_agent', methods=['POST'])
def register_agent():
    ip = request.form.get('ip')
    mac = request.form.get('mac')
    private_key_file = request.files.get('private_key')  # Obtener el archivo de la clave privada

    if not ip or not mac or not private_key_file:
        return jsonify({'error': 'Faltan IP, MAC o clave privada'}), 400

    # Leer el contenido binario del archivo .PEM
    private_key_content = private_key_file.read()

    # Guardar el contenido binario de la clave privada directamente en la "base de datos" (lista)
    agent = {
        'ip': ip,
        'mac': mac,
        'private_key': private_key_content  # Almacenamos en formato binario
    }

    # Almacenamos el agente en la lista
    agents.append(agent)

    return jsonify({'message': 'Agente registrado con éxito'}), 200

# Ruta para ver el archivo .PEM del agente
@app.route('/view_private_key/<int:agent_id>', methods=['GET'])
def view_private_key(agent_id):
    if agent_id < 0 or agent_id >= len(agents):
        return jsonify({'error': 'Agente no encontrado'}), 404
    
    # Obtener el agente y su clave privada
    agent = agents[agent_id]
    private_key_content = agent['private_key']

    # Crear un flujo de BytesIO con el contenido de la clave privada
    private_key_io = BytesIO(private_key_content)

    # Enviar el archivo como respuesta
    return send_file(private_key_io, as_attachment=True, download_name="rsa_private.pem", mimetype='application/x-pem-file')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)


