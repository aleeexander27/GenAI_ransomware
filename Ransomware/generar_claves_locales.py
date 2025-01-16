from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from os import remove

# Dividir datos en fragmentos seguros para RSA
def split_data(data, chunk_size):
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

# Generar clave privada
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048  
)

# Serializar y guardar la clave privada sin cifrar temporalmente
with open("private_key_temp.pem", "wb") as private_file:
    private_file.write(
        private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
    )

# Leer la clave pública desde el archivo previamente generado
with open("public_key.pem", "rb") as public_file:
    public_key = serialization.load_pem_public_key(public_file.read())

# Leer la clave privada temporal
with open("private_key_temp.pem", "rb") as private_file:
    private_key_data = private_file.read()

# Dividir la clave privada en fragmentos compatibles con RSA (190 bytes para 2048 bits con OAEP y SHA-256)
chunk_size = 190
private_key_chunks = split_data(private_key_data, chunk_size)

# Cifrar cada fragmento con la clave pública
encrypted_chunks = []
for chunk in private_key_chunks:
    if len(chunk) > 0:
        encrypted_chunk = public_key.encrypt(
            chunk,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        encrypted_chunks.append(encrypted_chunk)

# Combinar y guardar la clave privada cifrada en un archivo
with open("encrypted_private_key.pem", "wb") as encrypted_file:
    for chunk in encrypted_chunks:
        encrypted_file.write(chunk)

# Eliminar la clave privada sin cifrar
remove("private_key_temp.pem")

# Serializar y guardar la clave pública correspondiente a la nueva clave privada
with open("new_public_key.pem", "wb") as new_public_file:
    new_public_file.write(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    )

# Leer la clave privada (private_key.pem)
with open("private_key.pem", "rb") as private_key_file:
    private_key = serialization.load_pem_private_key(
        private_key_file.read(),
        password=None  # Si tiene contraseña, proporciónala aquí
    )

# Leer los datos cifrados desde el archivo
with open("encrypted_private_key.pem", "rb") as encrypted_file:
    encrypted_data = encrypted_file.read()

# Dividir los datos cifrados en fragmentos del tamaño esperado (256 bytes para RSA 2048 bits)
chunk_size = 256
encrypted_chunks = [encrypted_data[i:i + chunk_size] for i in range(0, len(encrypted_data), chunk_size)]

# Descifrar cada fragmento
decrypted_chunks = []
for chunk in encrypted_chunks:
    decrypted_chunk = private_key.decrypt(
        chunk,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    decrypted_chunks.append(decrypted_chunk)

# Combinar los fragmentos descifrados para obtener la clave privada original
decrypted_private_key = b"".join(decrypted_chunks)

# Guardar la clave privada descifrada
with open("decrypted_private_key.pem", "wb") as decrypted_file:
    decrypted_file.write(decrypted_private_key)