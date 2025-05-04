# Retraso evasivo en scripts

**Created:** 3/4/2025 20:23  

## Prompt:
Evitar técnicas de análisis automatizado implementando una función sleep que no use directamente time.sleep(), sino una alternativa más evasiva para retrasar la ejecución del script.

## Response:
Puedes implementar un retraso evasivo utilizando métodos alternativos en lugar de `time.sleep()`. Algunas estrategias incluyen:

1.  **Usar un bucle con cálculos ineficientes**  
    Ejecutar una operación costosa para desperdiciar tiempo sin llamar directamente a `sleep()`.
    
2.  **Usar `subprocess` para llamar a un comando externo**  
    Ejecutar un comando del sistema como `ping` o `timeout`.
    
3.  **Usar señales o eventos del sistema**  
    Esperar en eventos que no sean obvios para los análisis automatizados.
    

Aquí hay una implementación utilizando cálculos ineficientes y eventos:

```python
import random
import time
import threading

def evasive_sleep(seconds):
    start = time.perf_counter()
    while time.perf_counter() - start < seconds:
        _ = sum(random.randint(1, 100) for _ in range(10000))  # Cálculo inútil

# Alternativa con threading
def evasive_sleep_threaded(seconds):
    event = threading.Event()
    event.wait(timeout=seconds)

# Ejemplo de uso
evasive_sleep(5)  # Retrasa aproximadamente 5 segundos de forma evasiva
```

Esto hace que la ejecución se retrase sin un llamado explícito a `time.sleep()`, lo que puede dificultar su detección en análisis automatizados.

