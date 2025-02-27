from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

def generate_rsa_key():
    rsa_key = RSA.generate(2048)
    private_key = rsa_key.export_key()
    public_key = rsa_key.publickey().export_key()
    
    with open("rsa_private.pem", "wb") as priv_file:
        priv_file.write(private_key)
    
    with open("rsa_public.pem", "wb") as pub_file:
        pub_file.write(public_key)

def generate_aes_key():
    aes_key = get_random_bytes(32)  # 256 bits = 32 bytes
    with open("aes_key.bin", "wb") as aes_file:
        aes_file.write(aes_key)

if __name__ == "__main__":
    generate_rsa_key()
    generate_aes_key()