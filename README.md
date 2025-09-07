TODOFERRETERO 📱🔧

Aplicación móvil para la toma de pedidos offline, desarrollada en Python + Kivy, con almacenamiento en SQLite y generación de PDFs.
Compilada con Buildozer para ejecutarse en Android (probada en Android 14 – ZTE Blade A55).

🚀 Funcionalidades

Login seguro con usuarios desde SQLite.

Tomar pedidos offline asociados a clientes.

Historial de pedidos con búsqueda por nombre, RUT o número de orden.

Generación de PDFs de pedidos (con ReportLab).

Orientación fija en Portrait en Android.

Compatible con Scoped Storage (Android 11+).

📸 Capturas de pantalla

(agrega aquí tus imágenes en el repositorio, por ejemplo en /images/screenshots/ y enlázalas con markdown)

Ejemplo:






🛠️ Tecnologías utilizadas

Python 3.11.3

Kivy (interfaz gráfica y navegación entre pantallas)

SQLite (almacenamiento offline)

ReportLab (generación de PDFs)

Buildozer (compilación a APK para Android)

⚙️ Instalación y uso
1. Clonar el repositorio
git clone git@github.com:clarito2021/TODOFERRETERO.git
cd TODOFERRETERO

2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

3. Instalar dependencias (modo desarrollo en Mac/Linux/Windows)
pip install -r requirements-dev.txt

4. Ejecutar en desktop
python main.py

5. Compilar a Android APK

(requiere Docker o entorno de compilación Android configurado con Buildozer)

buildozer -v android debug
buildozer android deploy run

📂 Estructura del proyecto
TODOFERRETERO/
├── images/                 # Logo y recursos gráficos
├── bd_sqlite/              # Base de datos SQLite (local)
├── carrito.py              # Lógica de carrito de compras
├── historial.py            # Historial de pedidos
├── login.py                # Pantalla de login
├── main.py                 # Entrada principal de la app
├── pdf_pedido.py           # Generación de PDFs
├── resumen_cliente.py      # Resumen de cliente seleccionado
├── tomar_pedido.py         # Pantalla de toma de pedidos
├── requirements-dev.txt    # Dependencias para entorno local
└── .gitignore

👨‍💻 Autor

Carlos Reyes Bustamante
📧 citizenlex2016@gmail.com

🌐 GitHub – clarito2021

📜 Licencia

Este proyecto se distribuye bajo la licencia MIT.
Consulta el archivo LICENSE
 para más detalles.