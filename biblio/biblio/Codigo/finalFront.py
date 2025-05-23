from customtkinter import *
import tkinter as tk
from tkinter import Scrollbar, ttk, messagebox
from PIL import Image, ImageTk
import os
from Finalback import BibliotecaManager 
biblioteca_manager = BibliotecaManager()

root = None
administrar = None
botonPréstamo = None
fram_dev = None
mainfm = None
frame_gestionar_usuarios = None
entrtít = None
entredit = None
entrautor = None
entrgénero = None
biblioteca = None 
entr_búsqueda = None 
tree_usuarios_admin = None 
tree_devoluciones_admin = None 

#Imágenes
préstamo_img, gestionar_img, transferir_img, admin_img, búsqueda_img = None, None, None, None, None
añadir_img, devolución_img, retornar_img, usuarios_img, penalizar_img, reiniciar_pen_img = None, None, None, None, None, None

#Banderas
verificar_devolución = False
verificar_agregar = False
verificar_gestionar_usuarios = False


#Guardar libros
def guardar_nuevo_material_ui(): 
    global entrtít, entredit, entrautor, entrgénero

    if not all([entrtít, entredit, entrautor, entrgénero]):
        messagebox.showerror("Error", "Los campos de entrada no están inicializados.", parent=administrar if administrar and administrar.winfo_exists() else root)
        return

    nombre = entrtít.get().strip()
    editorial = entredit.get().strip()
    autor = entrautor.get().strip()
    género = entrgénero.get().strip()

    if not nombre or not editorial or not autor or not género:
        messagebox.showwarning("Campos vacíos", "Por favor, complete todos los campos.", parent=administrar if administrar and administrar.winfo_exists() else root)
        return

    success, message = biblioteca_manager.agregar_nuevo_libro(nombre, editorial, autor, género)
    if success:
        messagebox.showinfo("Éxito", message, parent=administrar if administrar and administrar.winfo_exists() else root)
        entrtít.delete(0, END)
        entredit.delete(0, END)
        entrautor.delete(0, END)
        entrgénero.delete(0, END)

        if root and root.winfo_exists() and not administrar: 
             cargar_datos_en_treeview_ui()
    else:
        messagebox.showerror("Error al Agregar", message, parent=administrar if administrar and administrar.winfo_exists() else root)


def desactivar_boton_prestamo():
    global botonPréstamo
    if botonPréstamo and botonPréstamo.winfo_exists():
        botonPréstamo.configure(state="disabled")

def activar_boton_prestamo():
    global botonPréstamo
    if botonPréstamo and botonPréstamo.winfo_exists():
        botonPréstamo.configure(state="normal")

#Seleccionar elemento
def al_seleccionar_libro_ui(event=None): 
    global biblioteca, botonPréstamo

    if not biblioteca or not biblioteca.winfo_exists():
        desactivar_boton_prestamo()
        return

    elementos_seleccionados = biblioteca.selection()

    if len(elementos_seleccionados) == 1:
        item_id = elementos_seleccionados[0]
        values = biblioteca.item(item_id, 'values') 

        if values:
            titulo_seleccionado = values[0] 
            libro_obj = biblioteca_manager.buscar_libro_por_titulo(titulo_seleccionado)
            if libro_obj and libro_obj.disponible:
                activar_boton_prestamo()
            else:
                desactivar_boton_prestamo()
        else:
            desactivar_boton_prestamo()
    else:
        desactivar_boton_prestamo()


#Confirmación de préstamo
def confirmar_prestamo_ui(ventana_usuario_toplevel, nombre_entrada_widget, libro_titulo_seleccionado): 
    global biblioteca 

    nombre_prestatario = nombre_entrada_widget.get().strip()

    if not nombre_prestatario:
        messagebox.showwarning("Campo vacío", "Por favor, ingresa el nombre del prestatario.", parent=ventana_usuario_toplevel)
        return

    success, message = biblioteca_manager.registrar_prestamo(libro_titulo_seleccionado, nombre_prestatario)

    if success:
        messagebox.showinfo("Préstamo Realizado", message, parent=ventana_usuario_toplevel)
        ventana_usuario_toplevel.destroy()
        cargar_datos_en_treeview_ui() 
        if verificar_gestionar_usuarios and tree_usuarios_admin and tree_usuarios_admin.winfo_exists():
            cargar_usuarios_en_treeview_admin_ui()
        if verificar_devolución and tree_devoluciones_admin and tree_devoluciones_admin.winfo_exists():
            cargar_libros_prestados_devolucion_ui()


    else:
        messagebox.showerror("Error de Préstamo", message, parent=ventana_usuario_toplevel)
        if "no encontrado" in message or "no está disponible" in message:
             ventana_usuario_toplevel.destroy()
        cargar_datos_en_treeview_ui() 

#Ventana de usuarios 
def ventana_usuario_ui(libro_titulo_seleccionado): 
    global root

    if not root or not root.winfo_exists():
        messagebox.showerror("Error", "La ventana principal no está disponible.", parent=root)
        return

    ventana_user = CTkToplevel(root)
    ventana_user.title("Ingresar Nombre del Prestatario")
    window_width = 350
    window_height = 200
    screen_width = ventana_user.winfo_screenwidth()
    screen_height = ventana_user.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    ventana_user.geometry(f"{window_width}x{window_height}+{x}+{y}")

    label_libro = CTkLabel(ventana_user, text=f"Prestando: '{libro_titulo_seleccionado}'", font=("Times New Roman", 14, "bold"))
    label_libro.pack(pady=(10, 5))

    label_nombre = CTkLabel(ventana_user, text="Nombre del Prestatario:", font=("Times New Roman", 12))
    label_nombre.pack(pady=(5, 0))

    nombre_user = CTkEntry(master=ventana_user, placeholder_text="Ingresa el nombre", width=250)
    nombre_user.pack(pady=(0, 10))
    nombre_user.focus_set()

    boton_confirmar = CTkButton(master=ventana_user, text="Confirmar Préstamo",
                                command=lambda: confirmar_prestamo_ui(ventana_user, nombre_user, libro_titulo_seleccionado))
    boton_confirmar.pack(pady=10)

    ventana_user.transient(root)
    ventana_user.grab_set()
    root.wait_window(ventana_user)


#Función principal de préstamo
def realizar_prestamo_ui():
    global biblioteca, root

    if not biblioteca or not biblioteca.winfo_exists():
        messagebox.showerror("Error", "El componente de biblioteca no está disponible.", parent=root)
        return

    elementos_seleccionados = biblioteca.selection()

    if not elementos_seleccionados:
        messagebox.showwarning("Sin selección", "Por favor, seleccione un libro.", parent=root)
        desactivar_boton_prestamo()
        return

    item_id_seleccionado = elementos_seleccionados[0] 
    titulo_seleccionado = item_id_seleccionado 
    libro_obj = biblioteca_manager.buscar_libro_por_titulo(titulo_seleccionado)

    if not libro_obj or not libro_obj.disponible:
        messagebox.showerror("Error", f"El libro '{titulo_seleccionado}' ya no está disponible.", parent=root)
        if biblioteca.winfo_exists() and biblioteca.exists(item_id_seleccionado):
            biblioteca.selection_remove(item_id_seleccionado) 
        cargar_datos_en_treeview_ui() 
        desactivar_boton_prestamo()
        return

    ventana_usuario_ui(titulo_seleccionado)


def cargar_datos_en_treeview_ui():
    global biblioteca

    if not biblioteca or not biblioteca.winfo_exists():
        return

    for item in biblioteca.get_children():
        biblioteca.delete(item)

    libros_disponibles = biblioteca_manager.get_libros_disponibles()
    
    libros_insertados = set() 
    for i, libro in enumerate(libros_disponibles):
        current_iid = libro.titulo

        if current_iid not in libros_insertados and not biblioteca.exists(current_iid):
            biblioteca.insert(parent='', index='end', iid=current_iid,
                                values=(libro.titulo, libro.editorial,
                                        libro.autor, libro.genero),
                                tags=('evenrow' if i % 2 == 0 else 'oddrow',))
            libros_insertados.add(current_iid)
        elif biblioteca.exists(current_iid):
             print(f"Advertencia (cargar_datos_en_treeview_ui): El libro con título (iid) '{current_iid}' ya existe en el Treeview. Se omitió la inserción duplicada.")
        else:
            print(f"Advertencia (cargar_datos_en_treeview_ui): Título de libro duplicado en los datos fuente: '{current_iid}'. Se omitió la inserción duplicada en el Treeview.")

    if biblioteca.selection(): 
        biblioteca.selection_remove(biblioteca.selection())
    desactivar_boton_prestamo()


#Búsqueda de libros
def buscar_libros_ui(event=None):
    global biblioteca, entr_búsqueda

    if not biblioteca or not biblioteca.winfo_exists() or not entr_búsqueda or not entr_búsqueda.winfo_exists():
        return

    query = entr_búsqueda.get().strip()

    for item in biblioteca.get_children():
        biblioteca.delete(item)

    libros_encontrados_objs = biblioteca_manager.buscar_libros_disponibles_por_termino(query)

    if not libros_encontrados_objs and query != '':
        messagebox.showinfo("Búsqueda", f"No se encontraron resultados para '{query}'", parent=root)

    libros_insertados_busqueda = set() 

    for i, libro in enumerate(libros_encontrados_objs):
        current_iid = libro.titulo
        if current_iid not in libros_insertados_busqueda and not biblioteca.exists(current_iid):
            biblioteca.insert(parent='', index='end', iid=current_iid,
                                values=(libro.titulo, libro.editorial,
                                        libro.autor, libro.genero),
                                tags=('evenrow' if i % 2 == 0 else 'oddrow',))
            libros_insertados_busqueda.add(current_iid)
        elif biblioteca.exists(current_iid):
            print(f"Advertencia (buscar_libros_ui): El libro con título (iid) '{current_iid}' ya existe en el Treeview. Se omitió la inserción duplicada.")
        else:
            print(f"Advertencia (buscar_libros_ui): Título de libro duplicado en los resultados de búsqueda: '{current_iid}'. Se omitió la inserción duplicada en el Treeview.")


    if biblioteca.selection():
        biblioteca.selection_remove(biblioteca.selection())
    desactivar_boton_prestamo()

#Ventana principal de la aplicación
def ventana_inicio():
    global root, biblioteca, botonPréstamo, entr_búsqueda
    global préstamo_img, gestionar_img, admin_img, búsqueda_img 

    if root is None or not root.winfo_exists():
        root = CTk()
        root.title("Biblioteca")
        set_appearance_mode("light")
        window_width = 900
        window_height = 650
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        root.protocol("WM_DELETE_WINDOW", on_closing_main_window_ui)

        title = CTkLabel(root, text="Biblioteca central", font=("Times New Roman", 40))
        title.pack(anchor="nw", padx=20, pady=10)
        
        try:
            base_path = os.path.dirname(os.path.abspath(__file__)) 
            img_path = os.path.join(base_path, "ima") 

            if gestionar_img is None and os.path.exists(os.path.join(img_path, "Gestionar.png")):
                imagen_gestionar_img = Image.open(os.path.join(img_path, "Gestionar.png")).resize((30, 30))
                gestionar_img = ImageTk.PhotoImage(imagen_gestionar_img)
            
            if admin_img is None and os.path.exists(os.path.join(img_path, "ajustes.png")):
                imagen_admin_img = Image.open(os.path.join(img_path, "ajustes.png")).resize((30, 30))
                admin_img = ImageTk.PhotoImage(imagen_admin_img)

            if búsqueda_img is None and os.path.exists(os.path.join(img_path, "lupa.png")):
                imagen_búsqueda_img = Image.open(os.path.join(img_path, "lupa.png")).resize((20, 20))
                búsqueda_img = ImageTk.PhotoImage(imagen_búsqueda_img)
        except Exception as e_img:
            print(f"Error al cargar imágenes para ventana_inicio: {e_img}")
        busqueaFrame = CTkFrame(root)
        busqueaFrame.pack(anchor = N, pady=10, fill="x", padx=20)

        entr_búsqueda = CTkEntry(busqueaFrame, placeholder_text="Buscar por Título, Autor o Género", width=600)
        entr_búsqueda.pack(side=LEFT, padx=(0,5), fill="x", expand=True)
        entr_búsqueda.bind("<Return>", buscar_libros_ui) 

        boton_buscar = CTkButton(busqueaFrame, image=búsqueda_img, text= '', width=30, height=30, command=buscar_libros_ui)
        boton_buscar.pack(side=LEFT)

        mainfm_treeview = CTkFrame(root,width=850, height=400)
        mainfm_treeview.pack(anchor = CENTER,pady=10, padx=20, expand=True, fill="both")

        tree_frame = CTkFrame(mainfm_treeview)
        tree_frame.pack(side="top", fill="both", expand=True)

        mainscroll = CTkScrollbar(tree_frame, command=None)
        mainscroll.pack(side = RIGHT, fill=Y)

        style = ttk.Style()
        style.theme_use("clam")
        
        bg_color_tree = "#EAEAEA"
        text_color_tree = "#1C1C1C"
        selected_color_tree = "#60A5FA"
        header_bg_color = "#D5D5D5"


        style.configure("Treeview",
                        rowheight=25,
                        fieldbackground=bg_color_tree, 
                        background=bg_color_tree, 
                        foreground=text_color_tree)
        style.map('Treeview', background=[('selected', selected_color_tree)], foreground=[('selected', text_color_tree)])
        style.configure("Treeview.Heading", font=('Arial', 11, 'bold'), background=header_bg_color, relief="flat")
        style.map("Treeview.Heading", relief=[('active','groove'),('pressed','sunken')])


        biblioteca = ttk.Treeview(tree_frame, columns = ('Título','Editorial','Autor','Género'), show='headings', yscrollcommand=mainscroll.set)
        mainscroll.configure(command=biblioteca.yview)

        biblioteca.heading('Título', text='Título', anchor='w') 
        biblioteca.column('Título', width=250, anchor='w', minwidth=150)
        biblioteca.heading('Editorial', text='Editorial', anchor='w')
        biblioteca.column('Editorial', width=200, anchor='w', minwidth=100)
        biblioteca.heading('Autor', text='Autor', anchor='w')
        biblioteca.column('Autor', width=200, anchor='w', minwidth=100)
        biblioteca.heading('Género', text='Género', anchor='center')
        biblioteca.column('Género', width=120, anchor='center', minwidth=80)

        biblioteca.pack(side="left", fill="both", expand=True)
        biblioteca.bind('<<TreeviewSelect>>', al_seleccionar_libro_ui)

        biblioteca.tag_configure('evenrow', background='#F0F0F0')
        biblioteca.tag_configure('oddrow', background='#FAFAFA')
        
        cargar_datos_en_treeview_ui() 

        frame_botones_laterales = CTkFrame(root, width=200)
        frame_botones_laterales.pack(side=LEFT, padx=(20,0), pady=(0,10), fill=Y, anchor="ne")

        botonPréstamo = CTkButton(master=frame_botones_laterales, text="Realizar préstamo", image=gestionar_img, state="disabled", command=realizar_prestamo_ui, compound="left", anchor="w")
        botonPréstamo.pack(pady=10, padx=10, fill="x")

        boton_admin = CTkButton(master=frame_botones_laterales, text="Administrar", image=admin_img, command=abrir_administracion_ui, compound="left", anchor="w") 
        boton_admin.pack(pady=10, padx=10, fill="x")
        
        desactivar_boton_prestamo()
        root.mainloop()
    else:
        root.deiconify()
        root.lift()
        cargar_datos_en_treeview_ui() 
        if entr_búsqueda and entr_búsqueda.winfo_exists():
            entr_búsqueda.delete(0, END)
        desactivar_boton_prestamo() 

def on_closing_main_window_ui():
    global root, administrar
    if messagebox.askokcancel("Salir", "¿Seguro que quieres salir de la aplicación?", parent=root):
        if administrar and administrar.winfo_exists():
            administrar.destroy() 
        if root:
            root.quit()
            root.destroy()



def limpiar_area_trabajo_admin_ui():
    global mainfm, fram_dev, frame_gestionar_usuarios
    if mainfm and mainfm.winfo_exists():
        mainfm.destroy()
        mainfm = None
    if fram_dev and fram_dev.winfo_exists():
        fram_dev.destroy()
        fram_dev = None
    if frame_gestionar_usuarios and frame_gestionar_usuarios.winfo_exists():
        frame_gestionar_usuarios.destroy()
        frame_gestionar_usuarios = None

#Verificar para limpiar el área de trabajo
def agregar_seccion_ui():
    global administrar, verificar_agregar, verificar_devolución, verificar_gestionar_usuarios, mainfm
    global entrtít, entredit, entrautor, entrgénero 

    if not administrar or not administrar.winfo_exists():
        return

    verificar_agregar = True
    verificar_devolución = False
    verificar_gestionar_usuarios = False
    limpiar_area_trabajo_admin_ui()

    mainfm = CTkFrame(administrar) 
    mainfm.pack(side=RIGHT, fill="both", expand=True, padx=20, pady=20)
    CTkLabel(mainfm, text="Agregar Nuevo Material", font=("Arial", 18, "bold")).pack(pady=10)

    CTkLabel(mainfm, text="Título:").pack(pady=(5,0), anchor="w", padx=10)
    entrtít = CTkEntry(mainfm, width=300)
    entrtít.pack(fill="x", padx=10)

    CTkLabel(mainfm, text="Editorial:").pack(pady=(5,0), anchor="w", padx=10)
    entredit = CTkEntry(mainfm, width=300)
    entredit.pack(fill="x", padx=10)

    CTkLabel(mainfm, text="Autor:").pack(pady=(5,0), anchor="w", padx=10)
    entrautor = CTkEntry(mainfm, width=300)
    entrautor.pack(fill="x", padx=10)

    CTkLabel(mainfm, text="Género:").pack(pady=(5,0), anchor="w", padx=10)
    entrgénero = CTkEntry(mainfm, width=300)
    entrgénero.pack(fill="x", padx=10)
    CTkButton(mainfm, text="Guardar Material", command=guardar_nuevo_material_ui).pack(pady=20)

def devolver_seccion_ui(): 
    global administrar, verificar_agregar, verificar_devolución, verificar_gestionar_usuarios, fram_dev, tree_devoluciones_admin
    
    if not administrar or not administrar.winfo_exists():
        return

    verificar_devolución = True
    verificar_agregar = False
    verificar_gestionar_usuarios = False
    limpiar_area_trabajo_admin_ui()

    fram_dev = CTkFrame(administrar) 
    fram_dev.pack(side=RIGHT, fill="both", expand=True, padx=20, pady=20)
    CTkLabel(fram_dev, text="Registrar Devoluciones", font=("Arial", 18, "bold")).pack(pady=10)
    # Treeview para devoluciones
    tree_devoluciones_frame = CTkFrame(fram_dev)
    tree_devoluciones_frame.pack(fill="both", expand=True, pady=10)
    
    tree_devoluciones_scroll = CTkScrollbar(tree_devoluciones_frame)
    tree_devoluciones_scroll.pack(side=RIGHT, fill=Y)

    style_admin = ttk.Style()
    style_admin.theme_use("clam") 
    style_admin.configure("Devolucion.Treeview", rowheight=25, fieldbackground="#EAEAEA", background="#EAEAEA", foreground="#1C1C1C")
    style_admin.map('Devolucion.Treeview', background=[('selected', '#60A5FA')])
    style_admin.configure("Devolucion.Treeview.Heading", font=('Arial', 10, 'bold'), background="#D5D5D5")

    cols_devolucion = ('Título', 'Autor', 'Prestatario')
    tree_devoluciones_admin = ttk.Treeview(tree_devoluciones_frame, columns=cols_devolucion, show='headings', style="Devolucion.Treeview", yscrollcommand=tree_devoluciones_scroll.set)
    tree_devoluciones_scroll.configure(command=tree_devoluciones_admin.yview)

    tree_devoluciones_admin.heading('Título', text='Título', anchor='w')
    tree_devoluciones_admin.column('Título', width=180, anchor='w', minwidth=100)
    tree_devoluciones_admin.heading('Autor', text='Autor', anchor='w')
    tree_devoluciones_admin.column('Autor', width=180, anchor='w', minwidth=100)
    tree_devoluciones_admin.heading('Prestatario', text='Prestatario', anchor='w')
    tree_devoluciones_admin.column('Prestatario', width=150, anchor='w', minwidth=100)
    tree_devoluciones_admin.pack(fill="both", expand=True, side=LEFT)
    
    cargar_libros_prestados_devolucion_ui()
    CTkButton(fram_dev, text="Registrar Devolución Seleccionada", command=registrar_devolucion_seleccionada_ui).pack(pady=10)

def cargar_libros_prestados_devolucion_ui():
    global tree_devoluciones_admin
    if not tree_devoluciones_admin or not tree_devoluciones_admin.winfo_exists():
        return
    for item in tree_devoluciones_admin.get_children():
        tree_devoluciones_admin.delete(item)
    
    libros_prestados_info = biblioteca_manager.get_libros_prestados_con_info()
    for libro_info in libros_prestados_info:
        tree_devoluciones_admin.insert('', 'end', iid=libro_info['titulo'], 
                                       values=(libro_info['titulo'], libro_info['autor'], libro_info['prestatario']))

def registrar_devolucion_seleccionada_ui():
    global tree_devoluciones_admin
    if not tree_devoluciones_admin or not tree_devoluciones_admin.winfo_exists(): return

    seleccion = tree_devoluciones_admin.selection()
    if not seleccion:
        messagebox.showwarning("Sin selección", "Seleccione un libro para registrar su devolución.", parent=administrar)
        return
    
    titulo_libro_devuelto = seleccion[0] 
    
    success, message = biblioteca_manager.registrar_devolucion(titulo_libro_devuelto)
    
    if success:
        messagebox.showinfo("Devolución Exitosa", message, parent=administrar)
        cargar_libros_prestados_devolucion_ui() 
        cargar_datos_en_treeview_ui() 
        if verificar_gestionar_usuarios and tree_usuarios_admin and tree_usuarios_admin.winfo_exists():
            cargar_usuarios_en_treeview_admin_ui()
    else:
        messagebox.showerror("Error de Devolución", message, parent=administrar)

#Gestión de usuarios en la ventana
def gestionar_usuarios_seccion_ui():
    global administrar, verificar_agregar, verificar_devolución, verificar_gestionar_usuarios, frame_gestionar_usuarios
    global tree_usuarios_admin, penalizar_img, reiniciar_pen_img 

    if not administrar or not administrar.winfo_exists():
        return

    verificar_gestionar_usuarios = True
    verificar_agregar = False
    verificar_devolución = False
    limpiar_area_trabajo_admin_ui()

    frame_gestionar_usuarios = CTkFrame(administrar)
    frame_gestionar_usuarios.pack(side=RIGHT, fill="both", expand=True, padx=20, pady=20)
    CTkLabel(frame_gestionar_usuarios, text="Gestionar Usuarios", font=("Arial", 18, "bold")).pack(pady=10)
    tree_usuarios_frame_container = CTkFrame(frame_gestionar_usuarios) 
    tree_usuarios_frame_container.pack(fill="both", expand=True, pady=(10,0)) 

    tree_usuarios_scroll = CTkScrollbar(tree_usuarios_frame_container)
    tree_usuarios_scroll.pack(side=RIGHT, fill=Y)

    style_admin_usr = ttk.Style()
    style_admin_usr.theme_use("clam")
    style_admin_usr.configure("Usuarios.Treeview", rowheight=25, fieldbackground="#EAEAEA", background="#EAEAEA", foreground="#1C1C1C")
    style_admin_usr.map('Usuarios.Treeview', background=[('selected', '#B0E0E6')])
    style_admin_usr.configure("Usuarios.Treeview.Heading", font=('Arial', 10, 'bold'), background="#D5D5D5")
    style_admin_usr.configure("Suspended.Treeview.Row", background="lightcoral", foreground="black")

    cols_usuarios = ('Nombre', 'Libros Prestados', 'Penalizaciones', 'Estado')
    tree_usuarios_admin = ttk.Treeview(tree_usuarios_frame_container, columns=cols_usuarios, show='headings', style="Usuarios.Treeview", yscrollcommand=tree_usuarios_scroll.set)
    tree_usuarios_scroll.configure(command=tree_usuarios_admin.yview)

    tree_usuarios_admin.heading('Nombre', text='Nombre', anchor='w')
    tree_usuarios_admin.column('Nombre', width=180, anchor='w', minwidth=120)
    tree_usuarios_admin.heading('Libros Prestados', text='Nº Libros', anchor='center')
    tree_usuarios_admin.column('Libros Prestados', width=80, anchor='center', minwidth=60)
    tree_usuarios_admin.heading('Penalizaciones', text='Penaliz.', anchor='center')
    tree_usuarios_admin.column('Penalizaciones', width=80, anchor='center', minwidth=60)
    tree_usuarios_admin.heading('Estado', text='Estado', anchor='center')
    tree_usuarios_admin.column('Estado', width=100, anchor='center', minwidth=80)

    tree_usuarios_admin.pack(fill="both", expand=True, side=LEFT)
    tree_usuarios_admin.tag_configure('suspendido', background='lightcoral', foreground='black')
    
    cargar_usuarios_en_treeview_admin_ui()

    botones_usr_frame = CTkFrame(frame_gestionar_usuarios)
    botones_usr_frame.pack(fill="x", pady=(5,10)) 

    try: 
        base_path = os.path.dirname(os.path.abspath(__file__))
        img_path_admin_icons = os.path.join(base_path, "ima")
        if penalizar_img is None and os.path.exists(os.path.join(img_path_admin_icons, "Penalizar.png")):
            imagen_penalizar_raw = Image.open(os.path.join(img_path_admin_icons, "Penalizar.png")).resize((20, 20))
            penalizar_img = ImageTk.PhotoImage(imagen_penalizar_raw)
        
        if reiniciar_pen_img is None and os.path.exists(os.path.join(img_path_admin_icons, "Reiniciar.png")):
            imagen_reiniciar_raw = Image.open(os.path.join(img_path_admin_icons, "Reiniciar.png")).resize((20,20))
            reiniciar_pen_img = ImageTk.PhotoImage(imagen_reiniciar_raw)
        elif reiniciar_pen_img is None:
            print("Advertencia: 'Reiniciar.png' no encontrado en la carpeta 'ima'.")
    except Exception as e_img_pen:
        print(f"Error al cargar icono en gestión de usuarios: {e_img_pen}")

    boton_penalizar = CTkButton(botones_usr_frame, text="Penalizar", image=penalizar_img, compound="left", command=penalizar_usuario_seleccionado_ui)
    boton_penalizar.pack(side=LEFT, padx=5, pady=5)

    boton_reiniciar_pen = CTkButton(botones_usr_frame, text="Reiniciar Penaliz.", image=reiniciar_pen_img, compound="left", command=reiniciar_penalizaciones_usuario_ui)
    boton_reiniciar_pen.pack(side=LEFT, padx=5, pady=5)


def cargar_usuarios_en_treeview_admin_ui():
    global tree_usuarios_admin
    if not tree_usuarios_admin or not tree_usuarios_admin.winfo_exists():
        return

    for item in tree_usuarios_admin.get_children():
        tree_usuarios_admin.delete(item)
    
    usuarios_info = biblioteca_manager.get_todos_los_usuarios_info()

    for usuario_data in usuarios_info:
        tags_usuario = ('suspendido',) if usuario_data['estado'] == "Suspendido" else ()
        tree_usuarios_admin.insert('', 'end', iid=usuario_data['nombre'], 
                                   values=(usuario_data['nombre'], 
                                           usuario_data['num_libros_prestados'], 
                                           usuario_data['penalizaciones'], 
                                           usuario_data['estado']),
                                   tags=tags_usuario) 

#Sistema de penalización
def penalizar_usuario_seleccionado_ui():
    global tree_usuarios_admin
    if not tree_usuarios_admin or not tree_usuarios_admin.winfo_exists(): return

    seleccion = tree_usuarios_admin.selection()
    if not seleccion:
        messagebox.showwarning("Sin selección", "Seleccione un usuario para penalizar.", parent=administrar)
        return
    
    nombre_usuario_seleccionado = seleccion[0] 
    
    confirmar = messagebox.askyesno("Confirmar Penalización", 
                                    f"¿Está seguro de que desea penalizar al usuario '{nombre_usuario_seleccionado}'?", 
                                    parent=administrar)
    if confirmar:
        success, message, _, _ = biblioteca_manager.penalizar_usuario(nombre_usuario_seleccionado)
        if success:
            messagebox.showinfo("Usuario Penalizado", message, parent=administrar)
            cargar_usuarios_en_treeview_admin_ui()
        else:
            messagebox.showerror("Error", message, parent=administrar)


def reiniciar_penalizaciones_usuario_ui():
    global tree_usuarios_admin
    if not tree_usuarios_admin or not tree_usuarios_admin.winfo_exists(): return

    seleccion = tree_usuarios_admin.selection()
    if not seleccion:
        messagebox.showwarning("Sin selección", "Seleccione un usuario para reiniciar sus penalizaciones.", parent=administrar)
        return
    
    nombre_usuario_seleccionado = seleccion[0]
            
    confirmar = messagebox.askyesno("Confirmar Reinicio", 
                                    f"¿Está seguro de que desea reiniciar las penalizaciones del usuario '{nombre_usuario_seleccionado}' a 0?", 
                                    parent=administrar)
    if confirmar:
        success, message = biblioteca_manager.reiniciar_penalizaciones_usuario(nombre_usuario_seleccionado)
        if success:
            messagebox.showinfo("Penalizaciones Reiniciadas", message, parent=administrar)
            cargar_usuarios_en_treeview_admin_ui()
        else:
            messagebox.showerror("Error", message, parent=administrar)


#Ventana de Administración
def abrir_administracion_ui(): 
    global root, administrar, verificar_devolución, verificar_agregar, verificar_gestionar_usuarios
    global añadir_img, devolución_img, retornar_img, usuarios_img 

    if not root or not root.winfo_exists():
        messagebox.showerror("Error", "La ventana principal no está disponible.", parent=root)
        return
    
    if administrar and administrar.winfo_exists():
        administrar.lift()
        return

    root.withdraw() 

    administrar = CTkToplevel(root) 
    administrar.title("Administración")
    window_width = 850
    window_height = 600
    screen_width = administrar.winfo_screenwidth()
    screen_height = administrar.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    administrar.geometry(f"{window_width}x{window_height}+{x}+{y}")
    administrar.protocol("WM_DELETE_WINDOW", retorno_a_principal_ui)

    fram_botones_admin = CTkFrame(administrar, width=220)
    fram_botones_admin.pack(side=LEFT, padx=10, pady=10, fill=Y)

    try: 
        base_path = os.path.dirname(os.path.abspath(__file__))
        img_path_admin_nav = os.path.join(base_path, "ima")

        if añadir_img is None and os.path.exists(os.path.join(img_path_admin_nav, "Añadir.png")): 
            imagen_añadir_img = Image.open(os.path.join(img_path_admin_nav, "Añadir.png")).resize((24, 24)) 
            añadir_img = ImageTk.PhotoImage(imagen_añadir_img)

        if devolución_img is None and os.path.exists(os.path.join(img_path_admin_nav, "Devolución.png")):
            imagen_devolución_img = Image.open(os.path.join(img_path_admin_nav, "Devolución.png")).resize((24, 24))
            devolución_img = ImageTk.PhotoImage(imagen_devolución_img)

        if retornar_img is None and os.path.exists(os.path.join(img_path_admin_nav, "devolver.png")):
            imagen_retornar_img = Image.open(os.path.join(img_path_admin_nav, "devolver.png")).resize((24, 24))
            retornar_img = ImageTk.PhotoImage(imagen_retornar_img)
        
        if usuarios_img is None and os.path.exists(os.path.join(img_path_admin_nav, "Usuarios.png")):
            imagen_usuarios_img_raw = Image.open(os.path.join(img_path_admin_nav, "Usuarios.png")).resize((24,24))
            usuarios_img = ImageTk.PhotoImage(imagen_usuarios_img_raw)
        elif usuarios_img is None:
             print("Advertencia: 'Usuarios.png' no encontrado en la carpeta 'ima'.")
    except Exception as e_img_admin_nav:
        print(f"Error al cargar imágenes para navegación de admin: {e_img_admin_nav}")

    boton_agregar_admin = CTkButton(master=fram_botones_admin, text="Agregar material", image=añadir_img, command=agregar_seccion_ui, compound="left", anchor="w")
    boton_agregar_admin.pack(pady=10, padx=10, fill="x")

    boton_devoluciones_admin = CTkButton(master=fram_botones_admin, text="Registrar devoluciones", image=devolución_img, command=devolver_seccion_ui, compound="left", anchor="w")
    boton_devoluciones_admin.pack(pady=10, padx=10, fill="x")

    boton_gestionar_usr_admin = CTkButton(master=fram_botones_admin, text="Gestionar Usuarios", image=usuarios_img, command=gestionar_usuarios_seccion_ui, compound="left", anchor="w")
    boton_gestionar_usr_admin.pack(pady=10, padx=10, fill="x")

    boton_retornar_admin = CTkButton(master=fram_botones_admin, text="Volver a Biblioteca", image=retornar_img, command=retorno_a_principal_ui, compound="left", anchor="w") 
    boton_retornar_admin.pack(pady=10, padx=10, fill="x", side="bottom") 
    
    agregar_seccion_ui() 

    administrar.transient(root)
    administrar.grab_set() 
    root.wait_window(administrar) 

#Función para retornar a la ventana principal
def retorno_a_principal_ui(): 
    global administrar, root, entr_búsqueda

    if administrar and administrar.winfo_exists():
        administrar.destroy()
        administrar = None

    limpiar_area_trabajo_admin_ui() 

    if root:
      if root.winfo_exists():
          root.deiconify()
          root.lift()
          cargar_datos_en_treeview_ui()
          if entr_búsqueda and entr_búsqueda.winfo_exists():
              entr_búsqueda.delete(0, END)
              entr_búsqueda.focus_set() 
          desactivar_boton_prestamo()
      else:
          root = None
          ventana_inicio() 
    else:
        ventana_inicio()

#Inicio de biblioteca
if __name__ == "__main__":
    ventana_inicio()