# Formatos de archivo adicionales

**Created:** 3/4/2025 17:40  

## Prompt:
aquí me podrías aportar más formatos: def es_archivo_importante(archivo):
    extensiones = {
        'imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        'vídeos': ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'],
        'música': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'documentos': ['.pdf', '.doc', '.docx',  '.odt','.txt',  '.rtf', '.xls', '.xlsx'],
        'bases de datos': ['.db', '.sqlite', '.sql', '.mdb'],
        'archivos comprimidos': ['.zip', '.rar', '.7z', '.tar', '.gz', '.tar.gz'],
        'extension_cifrada': ['.enc']
    }
    _, extension = os.path.splitext(archivo)
    return any(extension.lower() in ext_list for ext_list in extensiones.values())

## Response:
Aquí tienes la función con más formatos añadidos para cada categoría:

```python
import os

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
        'extension_cifrada': ['.enc', '.aes', '.gpg', '.pgp']
    }

    _, extension = os.path.splitext(archivo)
    return any(extension.lower() in ext_list for ext_list in extensiones.values())

# Ejemplo de uso:
print(es_archivo_importante("documento.pdf"))  # True
print(es_archivo_importante("video.xyz"))  # False
```

He agregado más formatos en cada categoría, incluyendo archivos ejecutables, archivos de código, archivos de configuración y archivos de diseño. 🚀



---
