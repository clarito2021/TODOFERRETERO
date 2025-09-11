<!-- markdownlint-disable-next-line MD041 -->
![Logo TODOFERRETERO](images/logo-todo-ferretero.jpg)

# 🛠️ Proyecto TODOFERRETERO ANDROID

# 📑 Índice

- [📌 Información General](#-información-general)
- [🛠️  Solicitudes Generales](#️--solicitudes-generales)
- [🚀 Funcionalidades Desarrolladas y probadas](#-funcionalidades-desarrolladas-y-probadas)
- [🚀 Funcionalidades NO Desarrolladas por cancelación del Proyecto](#-funcionalidades-no-desarrolladas-por-cancelación-del-proyecto)
- [🛠️ Tecnologías utilizadas](#️-tecnologías-utilizadas)
- [⚙️ Manual de Compilación y Ejecución](#️-manual-de-compilación-y-ejecución)
- [📂 Estructura del proyecto](#-estructura-del-proyecto)
- [📊 Diagramas de Flujo](#-diagramas-de-flujo)
- [🛢️ Consultas SQL](#️-consultas-sql)
- [📥 Descarga versión en desarrollo](#-descarga-versión-en-desarrollo)
- [📱 Capturas de pantalla en Android y 🎥 Videos de la aplicación](#-capturas-de-pantalla-en-android-y--videos-de-la-aplicación)
- [👨‍💻 Autor](#-autor)

<!-- /code_chunk_output -->

- [🛠️ Proyecto TODOFERRETERO ANDROID](#️-proyecto-todoferretero-android)
- [📑 Índice](#-índice)
- [📌 Información General](#-información-general)
- [🛠️  Solicitudes Generales](#️--solicitudes-generales)
- [🚀 Funcionalidades Desarrolladas y probadas](#-funcionalidades-desarrolladas-y-probadas)
- [🚀 Funcionalidades NO Desarrolladas por cancelación del Proyecto](#-funcionalidades-no-desarrolladas-por-cancelación-del-proyecto)
- [🛠️ Tecnologías utilizadas](#️-tecnologías-utilizadas)
- [⚙️ Manual de Compilación y Ejecución](#️-manual-de-compilación-y-ejecución)
- [📂 Estructura del proyecto](#-estructura-del-proyecto)
- [📊 Diagramas de Flujo](#-diagramas-de-flujo)
- [🛢️ Consultas SQL](#️-consultas-sql)
- [📥 Descarga versión en desarrollo](#-descarga-versión-en-desarrollo)
- [📱 Capturas de pantalla en Android y 🎥 Videos de la aplicación](#-capturas-de-pantalla-en-android-y--videos-de-la-aplicación)
- [👨‍💻 Autor](#-autor)

# 📌 Información General

- **Fecha de inicio generación de código**: 01/10/2025 13:30 hrs
- **Fecha de término**: 05/10/2025 14:00 hrs
- **Lenguaje de programación**: Python 3.11.3  (.venv)
- **Editor utilizado**: Visual Studio Code
- **Sistema operativo de desarrollo**: MacOS Sequoia 15.6.1 (con soporte para Linux/Windows)
- **Base de datos**: SQLite (`todoferre.db`)
- **Herramientas utilizadas**: DBeaver, CLI `sqlite3`
- **Cantidad de archivos de código**: 7 archivos .py

---------------------------------------------------------------------------------------------------------------

# 🛠️  Solicitudes Generales

- Aplicación móvil para la toma de pedidos **offline**
- La app debe trabajar con una base de datos **SQLite**
- La app debe poder actualizar los pedidos cuando tenga disponible una conexión a la internet
- desarrollada en **Python + Kivy**
- con almacenamiento en **SQLite** que debe poder actualizar tablas desde donde se obtiene información de clientes y productos
- generación de **PDFs** para el historial de las ordenes (tarea no. prioritaria)  
- Compilada con **Buildozer** para ejecutarse en **Android** (probada en Android 14 – ZTE Blade A55).

---------------------------------------------------------------------------------------------------------------

# 🚀 Funcionalidades Desarrolladas y probadas

- Login seguro con usuarios desde SQLite.
- Toma de pedidos **offline** asociados a clientes.  
- **Busqueda de Clientes dinámica**, con criterio de "Nombre de Fantasía", "Nombre Real", "RUT"
- Selección de precios (los precios son distintos dada la región), según **Criterio de Despacho**
- **Historial de pedidos** con búsqueda por "nombre", "RUT" o "número de orden".
- Carro de Compras (selector de productos para orden) con **Sesión Persistente**
- Validaciones ogligatorias para datos **Región** para configurar el "Despacho"
- Si el usuario no tiene dirección y escoge despacho, debe seleccionar una **region**
- Si no se completa la orden, **se mantiene una respaldo de la sesión de compras puede retomarse**
- Se se completa la orden, se eliminan los registros de sesiones incomopletas
- Generación de PDFs de pedidos (con **ReportLab**)
- Los PDF se muestran usando la app que tenga instalada el teléfono o tablet
- Orientación fija en **Portrait** en Android.  
- Compatible con **Scoped Storage** (Android 11+)

````
Notas del Desarrollo: 
Se probaron los casos de uso básicos, no se ejecutó un proceso profundo de Q.A, al entregar
la última compilación, se le informó a los solicitantes, este gran detalle, por lo tanto, 
si alguien retoma este proyecto debe considerar este proceso, puesto que hay tres etapas 
en el Q.A:

1. Q.A implícito en el desarrollo
2. Q.A ejecutado por un especialista en Q.A casos de uso generales + expansión
3. UAT, User Acceptance Test, ejecutado usuario + Especialista Q.A
````

# 🚀 Funcionalidades NO Desarrolladas por cancelación del Proyecto

- Sincronización de la tabla "orders" con un servicio On Line (Odoo)
- Actualización de las tablas "cliente", "usuarios", "pricelist", "products", desde servicio On Line (Odoo)
- Ajustes estéticos, dada la urgencia con la que se planteó el proyecto, se centró el desarrollo primero en funcionalidad
- No se llegó a tratar la calidad de los datos
- Se descubre que hay datos de cliente, no están completos
- La app, permite que haya datos vacios, como email
- Quedó pendiente, hacer una versión para Iphone, se priorizó Android
- No se hizo un Q.A Estricto
- Se detectaron errores en la primera compilación, que no se depuraron.

---------------------------------------------------------------------------------------------------------------

# 🛠️ Tecnologías utilizadas

-[Python 3.11.3](https://www.python.org/) (The official home of the Python Programming Language)

-[Kivy](https://kivy.org) (interfaz gráfica y navegación entre pantallas, MIT License)

-[SQLite](https://sqlite.org/) (almacenamiento offline)

-[ReportLab](https://www.reportlab.com) (generación de PDFs)

-[Buildozer](https://buildozer.readthedocs.io/en/latest/) (compilación a APK para Android)

- Es necesario usar un entorno virtual (`venv`):

    ```bash
        python3 -m venv .venv
        source .venv/bin/activate   # macOS/Linux
        .venv\Scripts\activate      # Windows
    ```

- Instalación de dependencias, se incluye lista de dependencias hasta el momento de la última compilación:
  
    ```bash
        pip install -r requirements-dev.txt
    ```

---------------------------------------------------------------------------------------------------------------

# ⚙️ Manual de Compilación y Ejecución

1. Clonar repositorio

    ```bash
        git clone git@github.com:clarito2021/TODOFERRETERO.git
        cd TODOFERRETERO
    ```

2. Crear entorno virtual

    ```bash
        python3 -m venv .venv
        source .venv/bin/activate
    ```

3. Instalar dependencias

    ```bash
        pip install -r requirements-dev.txt
    ```

    📦 Dependencias de Python (misma información contenida en requirements-dev.txt):

         - bcrypt==4.3.0
         - certifi==2025.8.3
         - charset-normalizer==3.4.3
         - docutils==0.22
         - et_xmlfile==2.0.0
         - idna==3.10
         - Kivy==2.3.0
         - Kivy-Garden==0.1.5
         - numpy==2.3.2
         - openpyxl==3.1.5
         - pandas==2.3.2
         - pillow==11.3.0
         - pip==25.2
         - Pygments==2.19.2
         - python-dateutil==2.9.0.post0
         - pytz==2025.2
         - reportlab==4.4.3
         - requests==2.32.5
         - setuptools==80.9.0
         - six==1.17.0
         - tzdata==2025.2
         - urllib3==2.5.0

4. Ejecutar en desktop

    ```bash
        python main.py
    ```

5. Compilar APK Android con Buildozer

    ```bash
        pip install buildozer
        buildozer -v android debug
        buildozer android deploy run
    ```

📌 Requiere Docker o entorno Android SDK/NDK configurado.

---------------------------------------------------------------------------------------------------------------

# 📂 Estructura del proyecto

        TODOFERRETERO/
        ├── images/                     # Directorio con Logo y recursos gráficos
        ├── bd_sqlite/                  # Directorio con Base de datos SQLite
        ├── login.py                    # Pantalla de login
        ├── carrito.py                  # Carrito de compras
        ├── historial.py                # Historial de pedidos
        ├── pdf_pedido.py               # Generación de PDFs
        ├── resumen_cliente.py          # Resumen de cliente
        ├── tomar_pedido.py             # Toma de pedidos
        ├── tools/                      # Directorio con Scripts de análisis
        │   ├── generate_mermaid.py
        │   ├── generate_drawio.py
        │   └── analyze_sql.py
        ├── docs/                       # Directorio con ocumentación y diagramas
        │   ├── flow_login.drawio
        │   ├── flow_carrito.drawio
        │   ├── flow_historial.drawio
        │   ├── flow_pdf_pedido.drawio
        │   ├── flow_resumen_cliente.drawio
        │   ├── flow_tomar_pedido.drawio
        │   ├── sql_insights.md
        │   └── screenshots/            # subdirectorio con Capturas de pantalla
        ├── requirements-dev.txt        # Archivo .TXT con Dependencias
        ├── buildozer.spec              # Intrucciones para compilar el APK
        └── main.py                     # Archivo simple que llama a login.py

---------------------------------------------------------------------------------------------------------------

# 📊 Diagramas de Flujo

El el siguiente link, se puede acceder a todos los diagramas ---> [Diagramas de Flujo](docs/FLOW_DOCS.md)

Ahí se ven los diagramas .drawio, png y una explicación de lo que hace cada módulo:

          - Login
          - Tomar pedido (tomar_pedido.py)
          - Resumen Cliente (resumen_cliente.py)Carrito
          - Historial (historial.py)
          - PDF Pedido (pdf_pedido.py)
          - Tomar Pedido (carrito.py)

---------------------------------------------------------------------------------------------------------------

# 🛢️ Consultas SQL

El archivo docs/sql_insights.md ---> [Consultas SQL](docs/SQL_DOCS.md)

Contiene el detalle de todas las consultas SQL que se hacen en el código de la app, incluyendo:

      - Tipo de operación (SELECT, INSERT, UPDATE, DELETE).

      - Tablas involucradas.

      - Campos consultados o modificados.

      - Condiciones y filtros.

      - ORDER BY y LIMIT cuando corresponden.

---------------------------------------------------------------------------------------------------------------

# 📥 Descarga versión en desarrollo

- [⬇️ Descargar APK](bin/todoferretero-0.1.0-arm64-v8a_armeabi-v7a-debug.apk)
- [📝 Notas de la versión v0.1.0](docs/release-notes-v0.1.0.md)

# 📱 Capturas de pantalla en Android y 🎥 Videos de la aplicación

El archivo docs/screenshots.md ---> 📱 [Screenshots Android](docs/screenshots.md)

Contiene algunas screehshots generales de la app instalada en Android

El archivo docs/videos.md ---> 🎥 [Demo de TODOFERRETERO en Android](docs/videos.md)

Contiene un video de la aplicación funcionando en un dispositvo Android

---------------------------------------------------------------------------------------------------------------

# 👨‍💻 Autor

Carlos Reyes Bustamante - Asistencia de Chat GPT (Chatcito)

📧 <citizenlex2016@gmail.com>

🌐 GitHub – clarito2021

📜 Licencia

Este proyecto no es de libre distribución.
