import os

def detectar_so():
    so = os.name
    if so == 'nt':
        return "Windows"
    elif so == 'posix':
        return "Linux"
    else:
        return None

def es_archivo_importante(archivo):
    extensiones = {
        'imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg', '.ico', '.heif', '.heic'],
        'vídeos': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv', '.3gp', '.mpeg', '.mpg'],
        'música': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.alac'],
        'documentos': ['.pdf', '.doc', '.docx', '.odt', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.md'],
        'bases de datos': ['.db', '.sqlite', '.sql', '.mdb', '.accdb', '.json', '.xml'],
        'archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz', '.bz2', '.xz', '.cab'],
        'archivos ejecutables': ['.exe', '.msi', '.bat', '.sh', '.apk', '.jar', '.bin', '.deb', '.rpm'],
        'archivos de código': ['.py', '.java', '.c', '.cpp', '.cs', '.js', '.html', '.css', '.php', '.swift', '.go', '.rs', '.ts'],
        'archivos de configuración': ['.ini', '.cfg', '.json', '.yaml', '.yml', '.toml', '.env'],
        'archivos de diseño': ['.psd', '.ai', '.xd', '.fig', '.sketch'],
        'extension_cifrada': ['.enc']
    }
    _, extension = os.path.splitext(archivo)
    return any(extension.lower() in ext_list for ext_list in extensiones.values())

def recorrer_directorio():
    so = detectar_so()
    if so == "Windows":
        directorio_base = os.environ.get('USERPROFILE', None)
    elif so == "Linux":
        directorio_base = os.environ.get('HOME', None)
    else:
        return "Sistema operativo no soportado."

    if not directorio_base:
        return "No se ha encontrado el directorio en la variable de entorno."

    directorio = os.path.join(directorio_base, 'Desktop', 'Files')
    if not os.path.isdir(directorio):
        return f"El directorio {directorio} no existe."

    archivos_importantes = []
    # Recorre directorios y subdirectorios recursivamente
    for root, _, files in os.walk(directorio):
        for file in files:
            if es_archivo_importante(file):
                archivos_importantes.append(os.path.relpath(os.path.join(root, file), directorio))

    return archivos_importantes  # Devuelve solo archivos importantes