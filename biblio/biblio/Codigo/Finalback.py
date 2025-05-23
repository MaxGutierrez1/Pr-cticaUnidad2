import json
import os

class Libro:
    def __init__(self, titulo, editorial, autor, genero, disponible=True, prestatario=None):
        self.titulo = titulo
        self.editorial = editorial
        self.autor = autor
        self.genero = genero
        self.disponible = disponible
        self.prestatario = prestatario 

     #funcion que identifica si esta prestado y a quien    
    def marcar_prestado(self, nombre_prestatario):
        if self.disponible:
            self.disponible = False
            self.prestatario = nombre_prestatario
            return True
        return False

    #funcion que identifica si esta devuelto
    def marcar_devuelto(self):
        self.disponible = True
        self.prestatario = None

    #Funcion para ipasar de objeto a diccionario y guardar en json
    def to_dict(self):
        return {
            'título': self.titulo,
            'editorial': self.editorial,
            'autor': self.autor,
            'género': self.genero,
            'disponibilidad': self.disponible,
            'prestatario': self.prestatario
        }

    # Funcion para pasar de diccionario a objeto
    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('título'),
            data.get('editorial'),
            data.get('autor'),
            data.get('género'),
            data.get('disponibilidad', True),
            data.get('prestatario')
        )

class Usuario:
    def __init__(self, nombre, libros_prestados=None, penalizaciones=0):
        self.nombre = nombre
        self.libros_prestados = libros_prestados if libros_prestados is not None else []
        self.penalizaciones = penalizaciones

    def agregar_libro_prestado(self, titulo_libro):
        if titulo_libro not in self.libros_prestados:
            self.libros_prestados.append(titulo_libro)

    def quitar_libro_prestado(self, titulo_libro):
        if titulo_libro in self.libros_prestados:
            self.libros_prestados.remove(titulo_libro)

    def incrementar_penalizacion(self):
        self.penalizaciones += 1

    def reiniciar_penalizaciones(self):
        self.penalizaciones = 0

    def esta_suspendido(self):
        return self.penalizaciones >= 3

    #Funcion para ipasar de objeto a diccionario y guardar en json
    def to_dict(self):
        return {
            'nombre': self.nombre,
            'libros_prestados': self.libros_prestados,
            'penalizaciones': self.penalizaciones
        }
    # Funcion para pasar de diccionario a objeto
    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get('nombre'),
            data.get('libros_prestados', []),
            data.get('penalizaciones', 0)
        )

class BibliotecaManager:
    def __init__(self, archivo_libros="librería.json", archivo_usuarios="users.json"):
        self.archivo_libros_path = archivo_libros
        self.archivo_usuarios_path = archivo_usuarios
        self.libros = []
        self.usuarios = []
        self._cargar_libros()
        self._cargar_usuarios()

    def _cargar_libros(self):
        try:
            if os.path.exists(self.archivo_libros_path):
                with open(self.archivo_libros_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.libros = [Libro.from_dict(item) for item in data]
            else:
                self.libros = []
        except (json.JSONDecodeError, FileNotFoundError):
            self.libros = [] 

    def _guardar_libros(self):
        with open(self.archivo_libros_path, 'w', encoding='utf-8') as f:
            json.dump([libro.to_dict() for libro in self.libros], f, ensure_ascii=False, indent=4)

    def _cargar_usuarios(self):
        try:
            if os.path.exists(self.archivo_usuarios_path):
                with open(self.archivo_usuarios_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.usuarios = [Usuario.from_dict(item) for item in data]
            else:
                self.usuarios = []
                self._guardar_usuarios() 
        except (json.JSONDecodeError, FileNotFoundError):
            self.usuarios = []

    def _guardar_usuarios(self):
        with open(self.archivo_usuarios_path, 'w', encoding='utf-8') as f:
            json.dump([usuario.to_dict() for usuario in self.usuarios], f, ensure_ascii=False, indent=4)

    def agregar_nuevo_libro(self, titulo, editorial, autor, genero):
        for libro_existente in self.libros:
            if libro_existente.titulo.lower() == titulo.lower() and \
               libro_existente.autor.lower() == autor.lower() and \
               libro_existente.editorial.lower() == editorial.lower():
                return False, "Este libro ya existe con el mismo autor y editorial."

        nuevo_libro = Libro(titulo, editorial, autor, genero)
        self.libros.append(nuevo_libro)
        self._guardar_libros()
        return True, f"Libro '{titulo}' agregado exitosamente."

    def buscar_libro_por_titulo(self, titulo, solo_disponibles=False):
        for libro in self.libros:
            if libro.titulo == titulo:
                if solo_disponibles:
                    return libro if libro.disponible else None
                return libro
        return None

    def buscar_usuario_por_nombre(self, nombre):
        for usuario in self.usuarios:
            if usuario.nombre == nombre:
                return usuario
        return None

    def registrar_prestamo(self, titulo_libro, nombre_prestatario):
        libro = self.buscar_libro_por_titulo(titulo_libro)
        if not libro:
            return False, f"Libro '{titulo_libro}' no encontrado."
        if not libro.disponible:
            return False, f"Libro '{titulo_libro}' no está disponible."

        usuario = self.buscar_usuario_por_nombre(nombre_prestatario)
        if usuario:
            if usuario.esta_suspendido():
                return False, f"Usuario '{nombre_prestatario}' está suspendido (penalizaciones: {usuario.penalizaciones})."
        else: 
            usuario = Usuario(nombre_prestatario)
            self.usuarios.append(usuario)

        libro.marcar_prestado(nombre_prestatario)
        usuario.agregar_libro_prestado(titulo_libro)
        
        self._guardar_libros()
        self._guardar_usuarios()
        return True, f"Préstamo de '{titulo_libro}' a '{nombre_prestatario}' registrado."

    def registrar_devolucion(self, titulo_libro_devuelto):
        libro_devuelto = None

        for libro_obj in self.libros:
            if libro_obj.titulo == titulo_libro_devuelto and not libro_obj.disponible:
                libro_devuelto = libro_obj
                break
        
        if not libro_devuelto:
            return False, f"Libro prestado con título '{titulo_libro_devuelto}' no encontrado o ya disponible."

        nombre_prestatario_dev = libro_devuelto.prestatario
        libro_devuelto.marcar_devuelto()

        if nombre_prestatario_dev:
            usuario = self.buscar_usuario_por_nombre(nombre_prestatario_dev)
            if usuario:
                usuario.quitar_libro_prestado(titulo_libro_devuelto)
        
        self._guardar_libros()
        self._guardar_usuarios()
        return True, f"Libro '{titulo_libro_devuelto}' devuelto."

    def penalizar_usuario(self, nombre_usuario):
        usuario = self.buscar_usuario_por_nombre(nombre_usuario)
        if not usuario:
            return False, f"Usuario '{nombre_usuario}' no encontrado.", 0, False
        
        usuario.incrementar_penalizacion()
        self._guardar_usuarios()
        suspendido = usuario.esta_suspendido()
        msg = f"Usuario '{nombre_usuario}' penalizado. Total: {usuario.penalizaciones}."
        if suspendido:
            msg += " ¡Usuario suspendido!"
        return True, msg, usuario.penalizaciones, suspendido

    def reiniciar_penalizaciones_usuario(self, nombre_usuario):
        usuario = self.buscar_usuario_por_nombre(nombre_usuario)
        if not usuario:
            return False, f"Usuario '{nombre_usuario}' no encontrado."
        
        if usuario.penalizaciones == 0:
            return True, f"Usuario '{nombre_usuario}' ya tiene 0 penalizaciones."

        usuario.reiniciar_penalizaciones()
        self._guardar_usuarios()
        return True, f"Penalizaciones de '{nombre_usuario}' reiniciadas a 0."

    def get_libros_disponibles(self):
        return [libro for libro in self.libros if libro.disponible]
    
    def get_libros_prestados_con_info(self):
        prestados_info = []
        for i, libro in enumerate(self.libros):
            if not libro.disponible:
                prestados_info.append({
                    'iid': str(i),
                    'titulo': libro.titulo,
                    'autor': libro.autor,
                    'prestatario': libro.prestatario
                })
        return prestados_info

    #Obtener la informacion del usuario requerido
    def get_todos_los_usuarios_info(self): 
        usuarios_info = []
        for usuario in self.usuarios:
            estado = "Suspendido" if usuario.esta_suspendido() else "Activo"
            usuarios_info.append({
                'nombre': usuario.nombre,
                'num_libros_prestados': len(usuario.libros_prestados),
                'penalizaciones': usuario.penalizaciones,
                'estado': estado
            })
        return usuarios_info

    def buscar_libros_disponibles_por_termino(self, query_raw):
        query = query_raw.strip().lower()
        if not query:
            return self.get_libros_disponibles() 

        encontrados = []
        for libro in self.libros:
            if libro.disponible:
                if query in libro.titulo.lower() or \
                   query in libro.autor.lower() or \
                   query in libro.genero.lower():
                    encontrados.append(libro)
        return encontrados