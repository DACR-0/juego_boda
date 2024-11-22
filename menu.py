import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pygame  # Librería para reproducir música

# Lógica para el juego principal
class DragDropGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Juego Personalizado")
        self.root.attributes('-fullscreen', True)  # Modo pantalla completa

        # Obtener el tamaño de la pantalla
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Crear el canvas principal
        self.canvas = tk.Canvas(self.root, bg="white", bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)  # Ajustar el Canvas a la pantalla

        # Dividir la pantalla en 35% y 65%
        self.left_area_width = int(self.screen_width * 0.22)
        self.right_area_width = self.screen_width - self.left_area_width

        # Cargar imagen de fondo
        self.bg_image = Image.open("fondo.jpg")  # Asegúrate de tener una imagen llamada "fondo.jpg"
        self.bg_image = self.bg_image.resize((self.right_area_width, self.screen_height))  # Redimensionar al 65% del tamaño de la pantalla
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)

        # Colocar la imagen de fondo en el canvas
        self.canvas.create_image(self.left_area_width, 0, image=self.bg_image_tk, anchor=tk.NW)

        # Cargar la imagen para los puestos
        self.puesto_image = Image.open("puesto.png")  # Asegúrate de tener una imagen llamada "puesto.png"
        self.puesto_image = self.puesto_image.resize((68, 68))  # Redimensionar la imagen del puesto
        self.puesto_image_tk = ImageTk.PhotoImage(self.puesto_image)

        # Variables para guardar casillas y nombres
        self.puestos_invitados = []
        self.estado_puestos = {}  # Diccionario para verificar ocupación por puesto
        self.nombres = {}
        self.origen_nombres = {}

        # Determinar la altura para cada zona de familia (50% de la altura total de la pantalla)
        familia_area_height = self.screen_height // 2

        # Dibujar las zonas de las familias
        self.dibujar_familia("Familia 1", 10, 50, ["Nombre 1", "Nombre 2"], "blue")  # Familia 1 en la parte superior
        self.dibujar_familia("Familia 2", 10, familia_area_height + 50, ["Nombre 3", "Nombre 4"], "green")  # Familia 2 en la parte inferior

        # Dibujar zona de invitados con 6 filas x 13 columnas, más separación y pasillo
        self.dibujar_zona_invitados(self.left_area_width + 20, familia_area_height -50, filas=6, columnas=15, tamaño=60, separación=16, pasillo_columna=7)
        self.dibujar_zona_invitados2(self.right_area_width -580 , familia_area_height -290 , filas=3, columnas=3, tamaño=60, separación=16, pasillo_columna=1)

        # Botón de salida
        tk.Button(self.root, text="Salir", command=self.root.quit, bg="red", fg="white").place(x=20, y=20)

    def dibujar_familia(self, nombre, x, y, nombres, color):
        # Dibujar marco de familia
        self.canvas.create_rectangle(x, y, x + 300, y + 400, outline="black", width=2)
        self.canvas.create_text(x + 100, y + 20, text=nombre, font=("Arial", 12, "bold"))

        # Dibujar nombres arrastrables
        for i, nombre in enumerate(nombres):
            label = tk.Label(self.root, text=nombre, bg=color, fg="white", width=10)
            label.place(x=x + 20, y=y + 40 + i * 30)
            self.nombres[label] = nombre  # Guardar referencia del nombre
            self.origen_nombres[label] = (x + 20, y + 40 + i * 30)  # Guardar posición inicial
            self.make_draggable(label)

    def dibujar_zona_invitados(self, x, y, filas, columnas, tamaño, separación, pasillo_columna):
        # Dibujar solo los puestos, sin el rectángulo de contenedor
        for i in range(filas):
            for j in range(columnas):
                if j == pasillo_columna:  # Crear un pasillo entre la columna 7 y 8
                    continue  # No dibujar casillas en la columna del pasillo

                x0 = x + j * (tamaño + separación)
                if j >= pasillo_columna:
                    x0 += tamaño + separación  # Ajustar la columna después del pasillo

                y0 = y + i * (tamaño + separación)

                # Colocar la imagen de la casilla (puesto)
                self.canvas.create_image(x0 + tamaño // 2, y0 + tamaño // 2, image=self.puesto_image_tk)

                # Guardar las posiciones de los puestos
                self.puestos_invitados.append((x0, y0))
                self.estado_puestos[(x0, y0)] = None  # Inicialmente el puesto está vacío

    def dibujar_zona_invitados2(self, x, y, filas, columnas, tamaño, separación, pasillo_columna):
        # Dibujar solo los puestos, sin el rectángulo de contenedor
        for i in range(filas):
            for j in range(columnas):
                if j == pasillo_columna:  # Crear un pasillo entre la columna específica
                    continue  # No dibujar casillas en la columna del pasillo

                # Calcular la posición inicial con el doble de separación
                x0 = x + j * (tamaño + 11 * separación)
                if j >= pasillo_columna:
                    x0 += tamaño + 2 * separación  # Ajustar la columna después del pasillo

                y0 = y + i * (tamaño + 1 * separación)

                # Colocar la imagen de la casilla (puesto)
                self.canvas.create_image(x0 + tamaño // 2, y0 + tamaño // 2, image=self.puesto_image_tk)

                # Guardar las posiciones de los puestos
                self.puestos_invitados.append((x0, y0))
                self.estado_puestos[(x0, y0)] = None  # Inicialmente el puesto está vacío


    def make_draggable(self, widget):
        widget.bind("<Button-1>", self.start_drag)
        widget.bind("<B1-Motion>", self.dragging)
        widget.bind("<ButtonRelease-1>", self.stop_drag)

    def start_drag(self, event):
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y
        # Al iniciar el arrastre, liberar el puesto si estaba ocupado
        for rect, ocupante in self.estado_puestos.items():
            if ocupante == widget:
                self.estado_puestos[rect] = None  # Liberar el puesto
                break

    def dragging(self, event):
        widget = event.widget
        x = widget.winfo_x() - widget.startX + event.x
        y = widget.winfo_y() - widget.startY + event.y
        widget.place(x=x, y=y)

    def stop_drag(self, event):
        widget = event.widget
        x = widget.winfo_x() + widget.winfo_width() / 2
        y = widget.winfo_y() + widget.winfo_height() / 2

        # Verificar si está sobre un puesto válido
        for x0, y0 in self.puestos_invitados:
            if x0 < x < x0 + 68 and y0 < y < y0 + 68:  # Verificar si la casilla está ocupada
                if not self.estado_puestos[(x0, y0)]:  # Verificar si el puesto está vacío
                    widget.place(x=x0 + 5, y=y0 + 5)  # Alinear al centro del puesto
                    self.estado_puestos[(x0, y0)] = widget  # Marcar el puesto como ocupado
                    return

        # Si no está en un puesto válido, devolverlo a su posición inicial
        orig_x, orig_y = self.origen_nombres[widget]
        widget.place(x=orig_x, y=orig_y)


# Menú principal con música
class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Menú Principal")
        self.root.attributes('-fullscreen', True)  # Modo pantalla completa

        # Configurar música
        pygame.mixer.init()
        pygame.mixer.music.load("musica.mp3")  # Cambia "musica.mp3" por el nombre de tu archivo de audio
        pygame.mixer.music.play(-1)  # Reproducir en bucle

        # Fondo de pantalla
        self.bg_image = Image.open("menu_fondo.jpg")  # Cambia "menu_fondo.jpg" por el nombre de tu imagen
        self.bg_image = self.bg_image.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.bg_image_tk = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight())
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, image=self.bg_image_tk, anchor=tk.NW)

        # Botón de inicio con estilo mejorado
        start_button = ttk.Button(self.root, text="Start", command=self.start_game, style="Start.TButton")
        start_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        # Estilo del botón
        self.style = ttk.Style()
        self.style.configure("Start.TButton",
                             font=("Arial", 18, "italic", "bold"),  # Fuente cursiva
                             padding=20,  # Espaciado interno para hacer el botón más grande
                             background="#ADD8E6",  # Fondo azul claro
                             foreground="#000fff",  # Texto en blanco
                             borderwidth=3,  # Borde del botón
                             relief="solid",  # Estilo de borde sólido
                             focuscolor="#ADD8E6",  # Color de enfoque del botón
                             highlightthickness=2,  # Grosor del borde al hacer foco
                             highlightbackground="black",  # Color de borde cuando el botón tiene foco
                             highlightcolor="black")  # Color de borde cuando se presiona

    def start_game(self):
        pygame.mixer.music.stop()  # Detener la música del menú
        self.root.destroy()  # Cerrar la ventana del menú
        launch_game()  # Lanzar el juego principal



# Función para lanzar el juego
def launch_game():
    root = tk.Tk()
    app = DragDropGame(root)
    root.mainloop()

# Crear la ventana del menú principal
root = tk.Tk()
menu = MainMenu(root)
root.mainloop()