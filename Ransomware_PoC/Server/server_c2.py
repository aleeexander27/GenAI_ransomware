from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Inicialización de Flask y SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///agents.db'  # Archivo SQLite para almacenar los agentes
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Definir el modelo de base de datos para los agentes
class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Número de agente (ID único)
    ip = db.Column(db.String(15), unique=True, nullable=False)  # IP del agente
    mac = db.Column(db.String(17), nullable=False)  # MAC del agente
    private_key = db.Column(db.Text, nullable=False)  # Clave privada del agente

    def __repr__(self):
        return f"<Agent {self.ip}>"

# Crear la base de datos (si no existe)
with app.app_context():
    db.create_all()

# Ruta principal que muestra la tabla con los agentes registrados
@app.route('/')
def index():
    agents = Agent.query.all()  # Obtener todos los agentes de la base de datos
    return render_template('index.html', agents=agents)

# Ruta para recibir los datos de los agentes (IP, MAC, y clave privada)
@app.route('/register_agent', methods=['POST'])
def register_agent():
    data = request.form
    ip = data.get('ip')
    mac = data.get('mac')
    private_key = data.get('private_key')

    if not ip or not mac or not private_key:
        return jsonify({'error': 'Faltan IP, MAC o clave privada'}), 400

    # Crear un nuevo agente y guardarlo en la base de datos
    new_agent = Agent(ip=ip, mac=mac, private_key=private_key)
    db.session.add(new_agent)
    db.session.commit()

    return jsonify({'message': 'Agente registrado con éxito'}), 200

# Ruta para obtener la información de un agente por su IP
@app.route('/get_agent_info/<agent_ip>', methods=['GET'])
def get_agent_info(agent_ip):
    # Buscar el agente en la base de datos
    agent = Agent.query.filter_by(ip=agent_ip).first()
    if not agent:
        return jsonify({'error': 'Agente no encontrado'}), 404

    return jsonify({
        'ip': agent.ip,
        'mac': agent.mac,
        'private_key': agent.private_key,
        'agent_id': agent.id
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

