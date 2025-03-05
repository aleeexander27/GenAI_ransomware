import psutil
import platform
import sys
import os
import sys
import re
import platform
import uuid
import ctypes
import signal
import time
import threading
import random

# Direcciones MAC de fabricantes de virtualización comunes
MAC_PREFIXES = {
    "VMware": ["00:50:56", "00:0C:29", "00:05:69"],
    "VirtualBox": ["08:00:27"],
    "Hyper-V": ["00:15:5D"],
    "QEMU/KVM": ["52:54:00"],
    "Parallels": ["00:1C:42"]
}

def get_mac_address():
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac.upper()

def check_hypervisor_mac(mac):
    for hypervisor, prefixes in MAC_PREFIXES.items():
        if any(mac.startswith(prefix) for prefix in prefixes):
            return hypervisor
    return None

def check_system_requirements():
    cpu_cores = psutil.cpu_count(logical=False)  #
    ram = psutil.virtual_memory().total / (1024 ** 3)  
    disk = psutil.disk_usage('/').total / (1024 ** 3)  

    if disk < 64 or ram < 4 or cpu_cores < 2:
        sys.exit(1)
    print("El sistema cumple con los requisitos mínimos.")

def is_debugger_present_windows():
    try:
        return ctypes.windll.kernel32.IsDebuggerPresent() != 0
    except AttributeError:
        return False

def detect_debuggers_windows():
    suspicious_processes = ["ollydbg", "ida", "ida64", "x64dbg", "dbgview", "wireshark"]
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            name = process.info['name'].lower()
            if any(susp in name for susp in suspicious_processes):
                print(f"[!] Depurador detectado: {name} (PID: {process.info['pid']})")
                os.kill(process.info['pid'], signal.SIGTERM)
                sys.exit(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def detect_debuggers_linux():
    suspicious_processes = ["gdb", "wireshark"]
    for process in psutil.process_iter(attrs=['pid', 'name']):
        try:
            name = process.info['name'].lower()
            if any(susp in name for susp in suspicious_processes):
                print(f"[!] Depurador detectado: {name} (PID: {process.info['pid']})")
                os.kill(process.info['pid'], signal.SIGTERM)
                sys.exit(1)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    try:
        with open("/proc/self/status", "r") as status_file:
            for line in status_file:
                if "TracerPid" in line:
                    if int(line.split()[1]) > 0:
                        print("[!] El proceso está siendo depurado mediante ptrace.")
                        sys.exit(1)
    except FileNotFoundError:
        pass

def evasive_sleep(seconds):
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        _ = sum(random.randint(1, 100) for _ in range(10000))  # Cálculo inútil

def check_virtualization_and_debbuging():
    evasive_sleep(10)
    if sys.platform.startswith("win"):
        if is_debugger_present_windows():
            print("[!] Depurador detectado mediante IsDebuggerPresent.")
            sys.exit(1)
        detect_debuggers_windows()
    elif sys.platform.startswith("linux"):
        detect_debuggers_linux()
    
    print("[+] No se detectaron depuradores. Continuando ejecución...")
    mac_address = get_mac_address()
    hypervisor = check_hypervisor_mac(mac_address)

    if hypervisor:
        print(f"El sistema está ejecutándose en un hipervisor: {hypervisor}")
        sys.exit(1)
    else:
        print("El sistema parece estar ejecutándose en hardware físico.")
    
    check_system_requirements()
    
    if __name__ == "__main__":
       check_virtualization_and_debbuging()