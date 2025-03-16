import psutil
import platform
import sys
import re
import uuid
import ctypes
import time
import random

MAC_PREFIXES = { 
        "VMware": ["00:50:56", "00:0C:29", "00:05:69"],
        "VirtualBox": ["08:00:27"],
        "Hyper-V": ["00:15:5D"],
        "QEMU/KVM": ["52:54:00"],
        "Parallels": ["00:1C:42"]
    }

def so_detection(): # Detección del sistema operativo
    sistema = platform.system()
    if sistema == "Windows":
        return "Windows"
    elif sistema == "Linux":
        return "Linux"
    else:
        sys.exit(1)  # Detiene el programa si no coincide con alguno de los SO 

def get_mac_address(): # Coger MAC de la primera interfaz de red 
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac.upper()

def check_hypervisor_mac(mac): # Comprobación de la MAC
    for hypervisor, prefixes in MAC_PREFIXES.items():
        if any(mac.startswith(prefix) for prefix in prefixes):
            print(f"[!] El sistema está ejecutándose en un hipervisor: {hypervisor}")
            sys.exit(1)  # Detiene el programa si se detecta un hipervisor
    return None

def check_system_requirements(): #Comprobación de requerimientos de hardware, si no cumple está en un entorno virtualizado
    cpu_cores = psutil.cpu_count(logical=False)  #
    ram = psutil.virtual_memory().total / (1024 ** 3)  
    disk = psutil.disk_usage('/').total / (1024 ** 3)  

    if disk < 64 or ram < 4 or cpu_cores < 2:
        sys.exit(1)

def is_debugger_present_windows():
    try:
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0
    except AttributeError:
        return False

def evasive_sleep(seconds): #retardo evasivo para engañar a los entornos de análisis
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        _ = sum(random.randint(1, 100) for _ in range(10000))  # Cálculo inútil y costoso a nivel de CPU

def check_virtualization_and_debugging():
    evasive_sleep(50)  # Implementación evasiva para detectar entornos de análisis
    so = so_detection()
    # Verificar depurador en Windows
    if so == "Windows":
        if is_debugger_present_windows():
            print("[!] Depurador detectado mediante IsDebuggerPresent.")
            sys.exit(1)
    # Comprobación de la MAC address para verificar hipervisores
    mac_address = get_mac_address()
    check_hypervisor_mac(mac_address)
    # Comprobación de recursos hardware 
    check_system_requirements()
    
if __name__ == "__main__":
    check_virtualization_and_debugging()