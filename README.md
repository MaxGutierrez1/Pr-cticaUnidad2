# Pr-cticaUnidad2
Sistema de Gestión de Biblioteca
Descripción General
Esta aplicación permite gestionar el préstamo y devolución de libros, así como la administración de usuarios y materiales disponibles. Utiliza una interfaz gráfica creada con CustomTkinter y una lógica de backend para manejar los datos mediante archivos JSON.
Inicio de la Aplicación
1. Ejecuta el archivo Biblioteca.exe
2. Se abrirá la ventana principal titulada “Biblioteca central”.
Funciones Principales
1. Buscar Libros
- Escribe el título, autor o género.
- Presiona Enter o haz clic en la lupa.

2. Realizar Préstamo
- Selecciona un libro.
- Haz clic en “Realizar préstamo”.
- Ingresa el nombre del prestatario.
- Confirma el préstamo.
Panel de Administración
Haz clic en “Administrar” para acceder a:

A. Agregar Material
- Llena los campos: Título, Editorial, Autor y Género.
- Haz clic en “Guardar Material”.

B. Registrar Devoluciones
- Selecciona un libro prestado.
- Haz clic en “Registrar Devolución Seleccionada”.

C. Gestionar Usuarios
- Penaliza usuarios.
- Reinicia penalizaciones.

D. Volver a Biblioteca
- Regresa a la interfaz principal.
Gestión de Usuarios y Reglas
- Penalizaciones se aplican manualmente.
- 3 penalizaciones => suspensión automática.
- Las penalizaciones pueden reiniciarse.
Datos y Almacenamiento
- Los libros se almacenan en librería.json.
- Los usuarios se almacenan en users.json.
- Los datos se cargan y guardan automáticamente.
Errores Comunes
- “Libro no disponible”: ya está prestado.
- “Usuario suspendido”: tiene 3 penalizaciones.
- “Campos vacíos”: asegúrate de llenar todos los campos.
