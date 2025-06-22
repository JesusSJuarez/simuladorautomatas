import tkinter as tk

class TapeDisplay(tk.Canvas):
    """
    Un widget de Tkinter para visualizar la cinta de la Máquina de Turing y la posición de la cabeza.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.cell_width = 40
        self.cell_height = 40
        self.tape_content = []
        self.head_position = 0
        self.center_offset = 0 # Offset para centrar la cabeza en la vista
        self.configure(bg='white', highlightbackground="gray", highlightthickness=1)

        self.bind("<Configure>", self._on_resize)
        self.bind("<ButtonPress-1>", self._on_button_press)
        self.bind("<B1-Motion>", self._on_mouse_drag)

    def _on_resize(self, event):
        """Maneja el redimensionamiento del canvas."""
        self.redraw()

    def _on_button_press(self, event):
        """Registra la posición inicial del arrastre del ratón."""
        self.last_x = event.x

    def _on_mouse_drag(self, event):
        """Maneja el arrastre del ratón para desplazar la cinta."""
        dx = event.x - self.last_x
        self.center_offset += dx
        self.last_x = event.x
        self.redraw()

    def set_tape(self, tape_content, head_position):
        """
        Establece el contenido de la cinta y la posición de la cabeza para visualización.

        Args:
            tape_content (list): Lista de símbolos en la cinta.
            head_position (int): Posición actual de la cabeza.
        """
        self.tape_content = tape_content
        self.head_position = head_position
        self.redraw()

    def redraw(self):
        """Redibuja la cinta en el canvas."""
        self.delete("all")
        
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        # Las variables y1 e y2 deben estar definidas siempre,
        # incluso si no hay contenido en la cinta para dibujar celdas.
        y1 = (canvas_height - self.cell_height) / 2
        y2 = y1 + self.cell_height

        # Calcular el índice de la celda central visible
        visible_center_index = self.head_position
        
        # Calcular el número de celdas visibles a cada lado del centro
        cells_to_display = int(canvas_width / self.cell_width)
        start_index_offset = int(cells_to_display / 2)

        # Calcular el índice inicial de la cinta a dibujar
        draw_start_index = visible_center_index - start_index_offset

        # Ajustar el offset de dibujo para centrar la cabeza
        # El centro del canvas es canvas_width / 2
        # La posición de la cabeza en el canvas si estuviera centrada sería (canvas_width / 2)
        # La posición real de la cabeza es (visible_center_index - draw_start_index) * self.cell_width
        
        # Calcular el desplazamiento para centrar la celda de la cabeza
        # Esto es para que la celda de la cabeza esté siempre en el centro de la vista
        # Ajustar el center_offset para que la cabeza se mantenga en el medio de la ventana
        # (canvas_width / 2) - ((self.head_position - draw_start_index) * self.cell_width + self.cell_width / 2)
        
        # Recalculamos draw_start_index para que la cabeza esté centrada o casi centrada
        # Queremos que self.head_position * self.cell_width esté cerca del centro del canvas_width
        # Esto es lo que ajusta el scroll de la cinta
        scroll_offset = self.center_offset % self.cell_width # Mantiene el arrastre suave
        
        # La celda de la cabeza debería estar en (canvas_width / 2)
        # Entonces, el inicio de la cinta en el canvas es:
        # canvas_start_x = (canvas_width / 2) - (self.head_position * self.cell_width)
        
        # Este es el centro visual del canvas
        visual_center_x = canvas_width / 2
        
        # Queremos que la celda de la cabeza esté en visual_center_x
        # La posición x de la celda de la cabeza es: x_offset + (self.head_position * self.cell_width)
        # Entonces, x_offset = visual_center_x - (self.head_position * self.cell_width)
        
        # Consideramos el center_offset para el arrastre
        start_x = visual_center_x - (self.head_position * self.cell_width) + self.center_offset
        
        for i in range(len(self.tape_content)):
            x1 = start_x + i * self.cell_width
            x2 = x1 + self.cell_width
            # y1 e y2 ya están calculadas antes del bucle
            # y1 = (canvas_height - self.cell_height) / 2
            # y2 = y1 + self.cell_height

            # Dibujar la celda
            self.create_rectangle(x1, y1, x2, y2, outline="black", fill="lightblue")
            
            # Dibujar el símbolo
            symbol = self.tape_content[i]
            self.create_text(x1 + self.cell_width / 2, y1 + self.cell_height / 2, text=symbol, font=("Arial", 14))

            # Resaltar la celda actual de la cabeza
            if i == self.head_position:
                self.create_rectangle(x1, y1, x2, y2, outline="red", width=3) # Borde rojo más grueso
                
                # Dibujar un triángulo para la cabeza
                triangle_y_top = y1 - 10
                triangle_y_bottom = y1
                self.create_polygon(x1 + self.cell_width / 2, triangle_y_top,
                                    x1 + self.cell_width / 2 - 10, triangle_y_bottom,
                                    x1 + self.cell_width / 2 + 10, triangle_y_bottom,
                                    fill="red", outline="red")
        
        # Dibujar líneas horizontales para la "pista"
        self.create_line(0, y1, canvas_width, y1, fill="gray", width=2)
        self.create_line(0, y2, canvas_width, y2, fill="gray", width=2)
