# Generación de claves RSA AES

**Created:** 4/2/2025 18:54  

## Prompt:
Genera un script en Python que cree una clave de cifrado RSA de 2048 bits y otra AES de 256 bits, con pycryptodome

## Response:
Aquí tienes un script en Python que genera una clave RSA de 2048 bits y una clave AES de 256 bits, y las guarda en archivos:

Generate Rsa Aes

```python
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
import os

def generate_rsa_key():
key = RSA.generate(2048)
private_key = key.export_key()
public_key = key.publickey().export_key()

with open("rsa_private.pem", "wb") as priv_file:
priv_file.write(private_key)

with open("rsa_public.pem", "wb") as pub_file:
pub_file.write(public_key)

print("RSA keys generated and saved.")

def generate_aes_key():
aes_key = os.urandom(32) # 256 bits (32 bytes)

with open("aes_key.bin", "wb") as aes_file:
aes_file.write(aes_key)

print("AES key generated and saved.")

if __name__ == "__main__":
generate_rsa_key()
generate_aes_key()

```

Responder en el chat en su lugar

Este script usa la biblioteca `pycryptodome` para generar y guardar una clave RSA de 2048 bits y una clave AES de 256 bits.  
Si no tienes `pycryptodome` instalado, puedes hacerlo con:

```sh
pip install pycryptodome
```

¿Necesitas alguna modificación o integración adicional? 🚀



---
