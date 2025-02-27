import os

def detectar_so():
    """
    Detecta el sistema operativo en el que se ejecuta el script.
    """
    so = os.name  # Obtiene el nombre del sistema operativo
    if so == 'nt':  # 'nt' indica que es Windows
        return "Windows"
    elif so == 'posix':  # 'posix' indica que es Linux
        return "Linux"
    else:
        return None

def es_archivo_importante(archivo):
    """
    Filtra los archivos importantes según su extensión.
    """
    # Definir extensiones comunes de archivos importantes
    extensiones = {
        'imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        'vídeos': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
        'música': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'documentos': ['.pdf', '.doc', '.docx', '.txt', '.odt', '.rtf', '.xls', '.xlsx'],
        'bases de datos': ['.db', '.sqlite', '.sql', '.mdb'],
        'archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz']
    }

    # Obtener la extensión del archivo
    _, extension = os.path.splitext(archivo)

    # Verificar si la extensión está en alguna de las categorías
    for categoria, ext_list in extensiones.items():
        if extension.lower() in ext_list:
            return True
    return False

def recorrer_directorio():
    """
    Recorre el directorio de usuario dependiendo del sistema operativo,
    usando las variables de entorno `USERPROFILE` (Windows) o `HOME` (Linux).
    Filtra y lista archivos importantes.
    """
    so = detectar_so()
    
    if so == "Windows":
        # Para Windows, utilizamos la variable de entorno USERPROFILE
        directorio_base = os.environ.get('USERPROFILE', None)
    elif so == "Linux":
        # Para Linux, utilizamos la variable de entorno HOME
        directorio_base = os.environ.get('HOME', None)
    else:
        return "Sistema operativo no soportado."

    if not directorio_base:
        return "No se ha encontrado el directorio en la variable de entorno."

    # Concatenamos Desktop/Files a la ruta base de manera común para ambos sistemas
    directorio = os.path.join(directorio_base, 'Desktop', 'Files')

    # Verifica si el directorio existe
    if not os.path.isdir(directorio):
        return f"El directorio {directorio} no existe."

    # Recorre el directorio y filtra archivos importantes
    archivos_importantes = []
    for archivo in os.listdir(directorio):
        ruta_archivo = os.path.join(directorio, archivo)
        if os.path.isfile(ruta_archivo) and es_archivo_importante(archivo):
            archivos_importantes.append(archivo)

    if archivos_importantes:
        return archivos_importantes
    else:
        return "No se encontraron archivos importantes en el directorio."

# Llamada a la función para recorrer el directorio
resultado = recorrer_directorio()
print(resultado)