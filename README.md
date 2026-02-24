# StockPro - Sistema de Gestión de Inventario para Pymes

StockPro es una aplicación web robusta diseñada para el control de inventario, permitiendo a las pequeñas y medianas empresas gestionar sus productos, monitorear niveles de stock crítico y exportar reportes detallados.



## Características de Seguridad (Nivel Profesional)
Este proyecto fue construido siguiendo estándares de seguridad de la industria:
* **Autenticación de Usuarios**: Acceso restringido mediante sesiones seguras con Flask-Login.
* **Hashing de Contraseñas**: Las credenciales no se almacenan en texto plano; se utiliza `Werkzeug` con algoritmos de derivación de claves (PBKDF2) para generar hashes seguros.
* **Protección de Rutas**: Implementación de decoradores `@login_required` para evitar accesos no autorizados a endpoints sensibles.
* **Variables de Entorno**: Uso de archivos `.env` para proteger la `SECRET_KEY` y datos de configuración, evitando su exposición en repositorios públicos.
* **Sanitización de Datos**: Prevención básica de inyecciones mediante el uso de parámetros en consultas SQL.

## Tecnologías Utilizadas
* **Backend**: Python 3.x, Flask.
* **Base de Datos**: SQLite3.
* **Frontend**: HTML5, CSS3 (Custom Styles), Bootstrap 5.
* **Reportes**: Pandas & Openpyxl (Exportación a Excel).
* **Gestión de Sesiones**: Flask-Login.

## Estructura del Proyecto
```text
GESTION_INVENTARIO/
├── app/                    # Lógica principal de la aplicación
│   ├── __init__.py         # Inicializador del paquete
│   └── routes.py           # Definición de rutas y endpoints
├── static/                 # Archivos estáticos (CSS, imágenes)
├── templates/              # Vistas HTML (Jinja2 templates)
├── .env                    # Variables de entorno (ignorado por Git)
├── .gitignore              # Configuración de archivos excluidos
├── crear_db.py             # Script de inicialización de base de datos
├── requirements.txt        # Dependencias del proyecto
└── run.py                  # Punto de entrada de la aplicación