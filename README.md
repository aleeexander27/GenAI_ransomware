# Ánalisis del uso de GenAI en la generación de ransomware con fines demostrativos, éticos y educativos
## Advertencia ⚠️
  -Este proyecto está orientado exclusivamente a fines educativos, demostrativos y de investigación en ciberseguridad.  
  -La ejecución de este código fuera de entornos controlados puede provocar la pérdida irreversible de datos.    
  -Está terminantemente prohibido su uso con fines malintencionados, en sistemas reales o sin consentimiento explícito.  

## Estructura del proyecto
Este repositorio contiene un prototipo funcional de ransomware dividido en dos partes:
- **Cliente:** Simula la ejecución del ransomware en un equipo víctima. Realiza el cifrado de archivos y se comunica con el servidor.
- **Servidor web (Flask):** Gestiona la conexión con el cliente y recibe información del cliente y su claves de cifrado.

## Requisitos
```bash
pip install -r requirements.txt