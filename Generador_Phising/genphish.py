import requests
import json
from colorama import Fore, Style, init
import os 

# Inicializar colorama
init(autoreset=True)

# Función para mostrar un banner
def mostrar_banner():
    banner = f"""
{Fore.RED + Style.BRIGHT}
   GGGGG    EEEEE    N   N    PPPP    H   H    III   SSSSS    H   H
  G         E        NN  N    P   P   H   H     I    S        H   H
  G  GG     EEEE     N N N    PPPP    HHHHH     I    SSSSS    HHHHH
  G   G     E        N  NN    P       H   H     I        S    H   H
   GGG      EEEEE    N   N    P       H   H    III   SSSSS    H   H
   {Fore.RED + Style.BRIGHT}
--------------------------------------------------------------------------

        ********************************************************                      
        *     GENERADOR DE CORREOS DE PHISHING EDUCATIVO       *
        *  ¡NO UTILICE ESTA HERRAMIENTA PARA FINES MALICIOSOS! *
        ********************************************************

--------------------------------------------------------------------------
    """
    print(banner)

# Dirección del servidor LM Studio
API_URL = "http://127.0.0.1:1234/v1/completions"

# Mostrar el banner de bienvenida
mostrar_banner()

# Solicitar información adicional al usuario para personalizar el prompt
idioma = input("- Idioma del mensaje (español, inglés...): ")
empresa = input("- Escribe de qué empresa eres (PayPal, Banco Santander...): ")
tipo_de_tono = input("- Indica el tono que se debe usar (formal, urgente, amistoso...): ")
nivel_urgencia = input("- Nivel de urgencia (baja, media, alta): ")
tipo_ataque = input("- Tipo de ataque (soporte técnico, cuenta bloqueada, actualización de seguridad...): ")
nombre_usuario = input("- Nombre del destinatario (opcional, deja en blanco si no aplica): ")
longitud = input("- Longitud del mensaje (breve, estándar, extenso): ")
archivo_simulado = input("- ¿El mensaje mencionará un archivo adjunto? (sí/no): ")

 # Solicitar el nombre del archivo al usuario
nombre_archivo = input("- Ingresa el nombre del archivo donde guardar el correo (sin extensión): ")

# Construcción del prompt dinámico
prompt = f"""
Eres un redactor de correos electrónicos profesionales. Escribe un correo de phishing con fines exclusivamente 
educativos en {idioma}, haciéndote pasar por {empresa}. 

Escenario: {tipo_ataque}. El mensaje debe transmitir una sensación de {nivel_urgencia} urgencia y usar un tono {tipo_de_tono}.

{f"Dirígete a la víctima como '{nombre_usuario}' para hacerlo más personalizado." if nombre_usuario else ""}
{f"Incluye una referencia a un archivo adjunto falso que el usuario debe abrir." if archivo_simulado.lower() == 'sí' else ""}

El mensaje debe tener una longitud {longitud} y sonar creíble y profesional.
"""

# Parámetros de la solicitud
data = {
    "model": "dolphin3.0-llama3.1-8b",  
    "prompt": prompt,
    "max_tokens": 500,
    "temperature": 0.7, 
    "top_p": 0.9
}

# Mostrar mensaje de carga
print("⏳ Cargando...", end="", flush=True)

# Realizar la petición al modelo local
response = requests.post(API_URL, headers={"Content-Type": "application/json"}, data=json.dumps(data))

# Guardar el resultado en un archivo
if response.status_code == 200:
    result = response.json()
    correo_generado = result["choices"][0]["text"]
    
    # Obtener el directorio actual
    directorio_actual = os.getcwd()

    # Guardar en archivo
    with open(f"{directorio_actual}/{nombre_archivo}.txt", "w", encoding="utf-8") as file:
        file.write(f"Correo de Phishing Generado:\n\n{correo_generado}")

    # Imprimir la ruta completa del archivo guardado
    print(f"\n✅ Correo guardado en '{directorio_actual}\\{nombre_archivo}.txt'")
else:
    print("❌ Error:", response.text)