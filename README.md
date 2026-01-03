[README.md](https://github.com/user-attachments/files/24417792/README.md)
# Editor de Partidas Guardadas de Hollow Knight

Este es un simple editor de partidas guardadas para Hollow Knight creado en Python. Te permite modificar tus archivos de guardado (`userX.dat`) para maximizar tus estadísticas, desbloquear objetos y obtener todas las habilidades.

## ¿Cómo usar el programa?

**Para la mayoría de los usuarios de Windows, se recomienda encarecidamente usar el archivo `.exe` para una experiencia más sencilla.**

Hay dos maneras de usar esta herramienta: ejecutando el archivo `.exe` (recomendado para la mayoría de los usuarios de Windows) o ejecutando el script de Python.

### Método 1: Usando el archivo `.exe` (Recomendado)

1.  **Descarga el archivo:** Ve a la [página principal del repositorio (releases)](https://github.com/marianonube-cpu/hollow-editor-save-game/releases/tag/hk) y descarga el archivo `hk_save_editor.exe`.
2.  **Ejecuta el programa:** Haz doble clic en `hk_save_editor.exe` para iniciarlo. Se abrirá una ventana de comandos.
3.  **Selecciona tu partida:** El programa intentará encontrar automáticamente tus archivos de guardado.
    *   Si los encuentra, te mostrará una lista. Simplemente escribe el número de la partida que quieres modificar y presiona `Enter`.
    *   Si no los encuentra, te pedirá que copies y pegues la ruta completa a tu archivo `user.dat`.
4.  **Elige una modificación:** El programa te mostrará un menú de opciones (maximizar vida, obtener todo el Geo, etc.). Escribe el número de la opción que desees y presiona `Enter`.
5.  **¡Listo!** El programa aplicará los cambios automáticamente. La próxima vez que inicies Hollow Knight, tu partida estará modificada.

**Nota:** El programa crea automáticamente una **copia de seguridad** de tu archivo de guardado original (con la extensión `.bak`) en la misma carpeta, por si algo sale mal o quieres revertir los cambios.

### Método 2: Usando el script de Python (para usuarios avanzados)

Si prefieres ejecutar el código fuente directamente, sigue estos pasos:

1.  **Requisitos:**
    *   Tener [Python 3](https://www.python.org/downloads/) instalado.
    *   Tener `git` instalado.

2.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/marianonube-cpu/hollow-editor-save-game.git
    cd hollow-editor-save-game
    ```

3.  **Instala las dependencias:**
    ```bash
    pip install pycryptodome
    ```

4.  **Ejecuta el script:**
    ```bash
    python hk_save_editor.py
    ```

5.  Sigue las mismas instrucciones que en el método del `.exe` para seleccionar tu partida y aplicar las modificaciones.

## Advertencia

Aunque el programa crea copias de seguridad, siempre es una buena práctica hacer un respaldo manual de tus archivos de guardado antes de modificarlos. El desarrollador no se hace responsable por la pérdida de datos.
