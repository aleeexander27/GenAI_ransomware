import os

# Lista de extensiones comunes para procesar
COMMON_EXTENSIONS = [
    '.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif',
    '.zip', '.rar', '.7z', '.tar', '.gz',
    '.mp3', '.wav', '.mp4', '.avi', '.mkv', '.mov',
    '.py', '.c', '.cpp', '.java', '.js', '.html', '.css'
]

def find_files_to_encrypt(base_directory):
    
    files_to_process = []

    for root, dirs, files in os.walk(base_directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in COMMON_EXTENSIONS):
                full_path = os.path.join(root, file)
                files_to_process.append(full_path)

    return files_to_process

if __name__ == "__main__":
    directory_to_scan = "C:\\Users\\alexander_tfg\\Desktop\\TFG\\Files"
    result_files = find_files_to_encrypt(directory_to_scan)

    if result_files:
        print("Archivos encontrados:")
        for file_path in result_files:
            print(file_path)
    else:
        print("No se encontraron archivos con extensiones comunes en el directorio especificado.")
