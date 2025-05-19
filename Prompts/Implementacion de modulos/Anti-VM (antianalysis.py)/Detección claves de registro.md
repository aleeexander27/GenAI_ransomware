# Detección claves de registro

**Created:** 5/16/2025 13:24  

## Prompt:
hazme un código que detecte si el código está siendo ejecutado en un entorno virtualizado según las claves de registro windows, si se encuentra devuelve true

## Response:
Aquí tienes un código en Python que detecta si se está ejecutando en un entorno virtualizado en Windows, revisando claves del Registro comunes que indican virtualización (como VMware, VirtualBox, Hyper-V, etc.):

```python
import winreg

def esta_virtualizado():
    claves_virtualizacion = [
        r"SYSTEM\CurrentControlSet\Services\VBoxGuest",     # VirtualBox
        r"SYSTEM\CurrentControlSet\Services\vmicheartbeat", # Hyper-V
        r"HARDWARE\ACPI\DSDT\VBOX__",                      # VirtualBox
        r"HARDWARE\DESCRIPTION\System",                   # General system info
        r"SOFTWARE\VMware, Inc.\VMware Tools",            # VMware
    ]

    cadenas_sospechosas = [
        "VBOX", "VirtualBox", "VMware", "Xen", "Virtual", "Hyper-V"
    ]

    for clave in claves_virtualizacion:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave)
            for i in range(0, winreg.QueryInfoKey(key)[1]):
                try:
                    nombre, valor, _ = winreg.EnumValue(key, i)
                    if any(palabra in str(valor) for palabra in cadenas_sospechosas):
                        return True
                except:
                    continue
            winreg.CloseKey(key)
        except FileNotFoundError:
            continue

    # Comprobar si el nombre del sistema contiene pistas
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System")
        for i in range(winreg.QueryInfoKey(key)[1]):
            nombre, valor, _ = winreg.EnumValue(key, i)
            if any(palabra in str(valor) for palabra in cadenas_sospechosas):
                return True
        winreg.CloseKey(key)
    except:
        pass

    return False

# Ejemplo de uso
if __name__ == "__main__":
    if esta_virtualizado():
        print("Entorno virtual detectado")
    else:
        print("No se detectó virtualización")
```

### Notas:

*   Necesita ejecutarse con privilegios de lectura del Registro (normalmente no necesita ser administrador).
    
*   Puedes ampliarlo incluyendo más claves o valores específicos para detectar entornos menos comunes.
    
*   No es 100% infalible; los entornos virtuales pueden ocultar su presencia.
    

¿Quieres que también revise el nombre del BIOS o información del hardware?

4o

## Prompt:
no entiendo el código hazlo más sencillo y limitate a lo que te solicité

## Response:
Perfecto, aquí tienes una versión **más sencilla y directa** del código que **solo verifica claves del registro** que suelen indicar virtualización y devuelve `True` si se encuentra alguna, como pediste:

```python
import winreg

def esta_virtualizado():
    claves = [
        r"SYSTEM\CurrentControlSet\Services\VBoxGuest",     # VirtualBox
        r"SYSTEM\CurrentControlSet\Services\vmicheartbeat", # Hyper-V
        r"SOFTWARE\VMware, Inc.\VMware Tools",              # VMware
    ]

    for clave in claves:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave)
            return True  # Clave encontrada, probablemente virtualizado
        except FileNotFoundError:
            continue

    return False
```

### ¿Cómo funciona?

*   Revisa 3 claves del registro que son típicas de entornos virtuales (VirtualBox, Hyper-V, VMware).
    
*   Si encuentra alguna, devuelve `True`.
    
*   Si no encuentra ninguna, devuelve `False`.
    

¿Quieres que también verifique otros entornos o dispositivos como Xen o QEMU?

4o

## Prompt:
añade más claves de registro

## Response:
Aquí tienes una versión **mejorada** del código, aún simple, pero con más claves de registro que pueden indicar ejecución en un entorno virtualizado (VirtualBox, VMware, Hyper-V, Parallels, Xen, etc.):

```python
import winreg

def esta_virtualizado():
    claves_virtualizacion = [
        # VirtualBox
        r"SYSTEM\CurrentControlSet\Services\VBoxGuest",
        r"HARDWARE\ACPI\DSDT\VBOX__",
        r"HARDWARE\ACPI\FADT\VBOX__",
        r"HARDWARE\ACPI\RSDT\VBOX__",

        # VMware
        r"SOFTWARE\VMware, Inc.\VMware Tools",
        r"SYSTEM\CurrentControlSet\Services\vmtools",
        r"SYSTEM\CurrentControlSet\Services\VMTools",

        # Hyper-V
        r"SYSTEM\CurrentControlSet\Services\vmicheartbeat",
        r"SYSTEM\CurrentControlSet\Services\vmicvss",
        r"SYSTEM\CurrentControlSet\Services\vmicshutdown",
        r"SYSTEM\CurrentControlSet\Services\vmicrdv",
        r"SYSTEM\CurrentControlSet\Services\vmictimesync",
        r"SYSTEM\CurrentControlSet\Services\vmicvmsession",

        # Parallels
        r"SYSTEM\CurrentControlSet\Services\prl_tools",

        # Xen
        r"SYSTEM\CurrentControlSet\Services\xenbus",
        r"SYSTEM\CurrentControlSet\Services\xenhide",

        # QEMU (raro, pero puede aparecer si está bien instalado)
        r"HARDWARE\ACPI\DSDT\QEMU__"
    ]

    for clave in claves_virtualizacion:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave)
            return True  # Se encontró una clave que indica virtualización
        except FileNotFoundError:
            continue

    return False
```

### Cómo usar:

Este código sigue siendo limpio, directo, y solo responde a tu requerimiento: buscar claves de registro específicas.  
Puedes ejecutarlo tal cual desde un script `.py`.

¿Te gustaría que también devuelva cuál de los entornos fue detectado?

4o

## Prompt:
okey los diccionarios ponlos fuera de la función

## Response:
Perfecto, aquí tienes el código actualizado con la lista de claves movida **fuera de la función**, como pediste:

```python
import winreg

# Lista de claves de registro que indican entornos virtualizados
CLAVES_VIRTUALIZACION = [
    # VirtualBox
    r"SYSTEM\CurrentControlSet\Services\VBoxGuest",
    r"HARDWARE\ACPI\DSDT\VBOX__",
    r"HARDWARE\ACPI\FADT\VBOX__",
    r"HARDWARE\ACPI\RSDT\VBOX__",

    # VMware
    r"SOFTWARE\VMware, Inc.\VMware Tools",
    r"SYSTEM\CurrentControlSet\Services\vmtools",
    r"SYSTEM\CurrentControlSet\Services\VMTools",

    # Hyper-V
    r"SYSTEM\CurrentControlSet\Services\vmicheartbeat",
    r"SYSTEM\CurrentControlSet\Services\vmicvss",
    r"SYSTEM\CurrentControlSet\Services\vmicshutdown",
    r"SYSTEM\CurrentControlSet\Services\vmicrdv",
    r"SYSTEM\CurrentControlSet\Services\vmictimesync",
    r"SYSTEM\CurrentControlSet\Services\vmicvmsession",

    # Parallels
    r"SYSTEM\CurrentControlSet\Services\prl_tools",

    # Xen
    r"SYSTEM\CurrentControlSet\Services\xenbus",
    r"SYSTEM\CurrentControlSet\Services\xenhide",

    # QEMU
    r"HARDWARE\ACPI\DSDT\QEMU__"
]

def esta_virtualizado():
    for clave in CLAVES_VIRTUALIZACION:
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, clave)
            return True  # Clave encontrada: indica virtualización
        except FileNotFoundError:
            continue

    return False
```

Este formato es más limpio si quieres mantener las configuraciones o listas separadas de la lógica. ¿Quieres ahora que identifique cuál de las claves fue encontrada o prefieres que simplemente devuelva `True`/`False` como hasta ahora?

4o



---
