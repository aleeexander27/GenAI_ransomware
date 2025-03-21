from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes

def generate_rsa_key(): # Generación par de claves RSA
    rsa_key = RSA.generate(2048) 
    private_key = rsa_key.export_key()
    public_key = rsa_key.publickey().export_key()
    with open("rsa_private.pem", "wb") as priv_file:
        priv_file.write(private_key)
    with open("rsa_public.pem", "wb") as pub_file:
        pub_file.write(public_key)

def generate_aes_key(): # Generación clave AES
    aes_key = get_random_bytes(32)  
    with open("aes_key.bin", "wb") as aes_file:
        aes_file.write(aes_key)




