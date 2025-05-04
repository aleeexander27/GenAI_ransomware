# Detectar hipervisor por MAC

**Created:** 3/4/2025 16:22  

## Prompt:
Detectar si el script está ejecutándose en un hipervisor según la dirección MAC en Windows y Linux,

## Response:
Puedes detectar si un script se está ejecutando dentro de un hipervisor verificando la dirección MAC de la interfaz de red. Muchas máquinas virtuales utilizan rangos de direcciones MAC específicas asignadas por los fabricantes de hipervisores.

### Paso 1: Lista de prefijos MAC de hipervisores comunes

Los hipervisores suelen asignar direcciones MAC con los siguientes prefijos:

*   **VMware**: `00:50:56`, `00:0C:29`, `00:05:69`
    
*   **VirtualBox**: `08:00:27`
    
*   **Hyper-V**: `00:15:5D`
    
*   **QEMU/KVM**: `52:54:00`
    
*   **Parallels**: `00:1C:42`
    

### Paso 2: Obtener la dirección MAC y verificarla

#### **En Windows (PowerShell)**

```powershell
$mac = (Get-NetAdapter | Select-Object -ExpandProperty MacAddress) -match "([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}"
$mac_prefixes = @("00:50:56", "00:0C:29", "00:05:69", "08:00:27", "00:15:5D", "52:54:00", "00:1C:42")

foreach ($prefix in $mac_prefixes) {
    if ($mac -like "$prefix*
```

## Prompt:
debe ser un script en python

## Response:
Aquí tienes un script en **Python** para detectar si el sistema se está ejecutando en un hipervisor según la dirección MAC en **Windows y Linux**:

### **Código en Python**:

```python
import re
import uuid

# Lista de prefijos MAC de hipervisores comunes
MAC_PREFIXES = {
    "VMware": ["00:50:56", "00:0C:29", "00:05:69"],
    "VirtualBox": ["08:00:27"],
    "Hyper-V": ["00:15:5D"],
    "QEMU/KVM": ["52:54:00"],
    "Parallels": ["00:1C:42"]
}

def get_mac_address():
    """Obtiene la dirección MAC de la interfaz de red principal."""
    mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
    return mac.upper()

def check_hypervisor_mac(mac):
    """Verifica si la dirección MAC pertenece a un hipervisor."""
    for hypervisor, prefixes in MAC_PREFIXES.items():
        if any(mac.startswith(prefix) for prefix in prefixes):
            return hypervisor
    return None

if __name__ == "__main__":
    mac_address = get_mac_address()
    hypervisor = check_hypervisor_mac(mac_address)

    if hypervisor:
        print(f"El sistema está ejecutándose en un hipervisor: {hypervisor}")
    else:
        print("El sistema parece estar ejecutándose en hardware físico.")
```

### **Explicación**:

1.  Se obtiene la dirección MAC de la interfaz de red principal usando `uuid.getnode()`.
    
2.  Se convierte la dirección MAC a formato estándar (`XX:XX:XX:XX:XX:XX`).
    
3.  Se compara el prefijo MAC con una lista de fabricantes de hipervisores.
    
4.  Si hay coincidencia, se indica en qué hipervisor se está ejecutando.
    

### **Ejemplo de salida**:

*   En una VM de **VirtualBox**:
    
    ```
    El sistema está ejecutándose en un hipervisor: VirtualBox
    ```
    
*   En una máquina física:
    
    ```
    El sistema parece estar ejecutándose en hardware físico.
    ```
    

Este script funciona tanto en **Windows como en Linux** sin dependencias adicionales. 🚀

## Prompt:
todo esto se puede unir en uno: if disk < 64:
        print("Error: Se requiere al menos 64 GB de almacenamiento.")
        sys.exit(1)
    if ram < 4:
        print("Error: Se requiere al menos 4 GB de RAM.")
        sys.exit(1)
    if cpu_cores < 2:
        print("Error: Se requieren al menos 2 núcleos físicos de CPU.")
        sys.exit(1)

## Response:
Sí, puedes combinar todas las condiciones en una sola estructura `if` usando el operador `or`, de esta forma:

```python
import sys

if disk < 64 or ram < 4 or cpu_cores < 2:
    if disk < 64:
        print("Error: Se requiere al menos 64 GB de almacenamiento.")
    if ram < 4:
        print("Error: Se requiere al menos 4 GB de RAM.")
    if cpu_cores < 2:
        print("Error: Se requieren al menos 2 núcleos físicos de CPU.")
    sys.exit(1)
```

### **Explicación**:

*   Se usa `or` para comprobar si alguna de las condiciones no se cumple.
    
*   Si alguna es falsa, se imprimen solo los mensajes de error correspondientes.
    
*   Se usa `sys.exit(1)` después de imprimir los errores para detener la ejecución.
    

Este enfoque es más eficiente y evita múltiples llamadas a `sys.exit(1)`. 🚀



---
