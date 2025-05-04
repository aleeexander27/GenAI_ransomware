# Evaluar importancia de archivos

**Created:** 3/4/2025 14:46  

## Prompt:
Genera una función que dado un archivo considere si es importante en cuanto a información según su extensión
(imágenes, vídeos, música, documentos, bases de datos, archivos comprimidos...).

## Response:
Para generar una función que determine si un archivo es "importante" según su extensión, podemos basarnos en ciertas categorías de archivos comunes, como imágenes, vídeos, documentos, bases de datos, música y archivos comprimidos. La función puede asignar un peso o prioridad a cada tipo de archivo y determinar si ese archivo es importante en función de su extensión.

A continuación, te muestro un ejemplo en Python:

```python
import os

def es_archivo_importante(archivo):
    # Lista de extensiones de archivos que consideramos "importantes"
    extensiones_importantes = {
        'imágenes': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg'],
        'vídeos': ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm'],
        'música': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
        'documentos': ['.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx', '.odt'],
        'bases_de_datos': ['.db', '.sql', '.sqlite', '.mdb'],
        'archivos_comprimidos': ['.zip', '.rar', '.tar', '.gz', '.7z']
    }
    
    # Obtener la extensión del archivo
    _, extension = os.path.splitext(archivo)
    extension = extension.lower()  # Convertir a minúsculas para evitar problemas de mayúsculas/minúsculas

    # Verificar en qué categoría entra el archivo
    for categoria, extensiones in extensiones_importantes.items():
        if extension in extensiones:
            return True  # El archivo es importante

    return False  # El archivo no es importante

# Ejemplos de uso
archivos = ["foto.jpg", "video.mp4", "documento.pdf", "archivo.rar", "musica.mp3", "archivo.txt", "notimportant.xyz"]

for archivo in archivos:
    if es_archivo_importante(archivo):
        print(f"El archivo {archivo} es importante.")
    else:
        print(f"El archivo {archivo} no es importante.")
```

### Explicación:

1.  **Categorías de Archivos**: Se define un diccionario `extensiones_importantes` que categoriza diferentes tipos de archivos según su extensión (imágenes, vídeos, música, documentos, bases de datos, archivos comprimidos).
    
2.  **Función `es_archivo_importante`**: Esta función recibe el nombre del archivo, obtiene su extensión y verifica si esa extensión pertenece a alguna de las categorías definidas en el diccionario.
    
3.  **Uso de la función**: Se muestra cómo usar esta función con una lista de archivos para determinar si son importantes o no.
    

### Salida esperada:

```
El archivo foto.jpg es importante.
El archivo video.mp4 es importante.
El archivo documento.pdf es importante.
El archivo archivo.rar es importante.
El archivo musica.mp3 es importante.
El archivo archivo.txt no es importante.
El archivo notimportant.xyz no es importante.
```

### Expansión:

Puedes añadir más categorías o extensiones según sea necesario, dependiendo de las necesidades de tu aplicación. Además, puedes personalizar la lógica para que el archivo no solo sea importante por su extensión, sino también por otros criterios como su tamaño o su contenido.



---
