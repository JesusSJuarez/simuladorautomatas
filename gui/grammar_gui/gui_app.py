import tkinter as tk
from tkinter import scrolledtext, messagebox, END, Toplevel, Canvas
from core.grammar_simulator import CFGSimulator
from gui.grammar_gui.derivation_tree_generator import build_parse_tree

class CFGSimulatorApp:
    """
    Clase para la aplicación de interfaz gráfica del Simulador de Gramáticas Libres de Contexto.
    """
    def __init__(self, root):
        """
        Inicializa la aplicación Tkinter.

        Args:
            root (tk.Tk): La ventana principal de Tkinter.
        """
        self.root = root
        self.root.title("Simulador de Gramáticas Libres de Contexto")
        self.root.geometry("800x700") # Tamaño inicial de la ventana

        # Lista para almacenar la historia detallada de la derivación para la construcción del árbol
        self.derivation_log = []

        # Configurar el simulador
        self.simulator = CFGSimulator(
            self.display_step,
            self.ask_for_choice,
            self.display_message,
            self.clear_choices_buttons
        )

        self._create_widgets()
        self.current_choice_buttons = [] # Para almacenar referencias a los botones de elección

    def _create_widgets(self):
        """
        Crea y organiza todos los widgets de la interfaz gráfica.
        """
        # --- Sección de Configuración de la Simulación ---
        config_frame = tk.LabelFrame(self.root, text="Configuración de la Simulación", padx=10, pady=10)
        config_frame.pack(pady=10, padx=10, fill="x")

        # Reglas de Producción
        tk.Label(config_frame, text="Reglas de Producción (ej: S->aSb | ε):").pack(anchor="w", pady=(0, 5))
        self.rules_input = scrolledtext.ScrolledText(config_frame, width=70, height=8, wrap=tk.WORD,
                                                     font=('Arial', 10), bd=2, relief="groove")
        self.rules_input.insert(END, "S->aSb\nS->ε\n") # Ejemplo
        self.rules_input.pack(pady=5, fill="x")
        tk.Label(config_frame, text="Formato: `NoTerminal->Producción1 | Producción2`. Use `ε` para la cadena vacía.",
                 font=('Arial', 8), fg='gray').pack(anchor="w")

        # Símbolo Inicial y Cadena a Simular
        input_frame = tk.Frame(config_frame)
        input_frame.pack(pady=5, fill="x")

        tk.Label(input_frame, text="Símbolo Inicial:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.start_symbol_input = tk.Entry(input_frame, width=10, font=('Arial', 10), bd=2, relief="groove")
        self.start_symbol_input.insert(0, "S")
        self.start_symbol_input.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        tk.Label(input_frame, text="Un solo carácter, generalmente una letra mayúscula.",
                 font=('Arial', 8), fg='gray').grid(row=1, column=0, columnspan=2, sticky="w", padx=5)

        tk.Label(input_frame, text="Cadena a Simular:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.target_string_input = tk.Entry(input_frame, width=30, font=('Arial', 10), bd=2, relief="groove")
        self.target_string_input.insert(0, "aabb") # Ejemplo
        self.target_string_input.grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        tk.Label(input_frame, text="La cadena que desea derivar.",
                 font=('Arial', 8), fg='gray').grid(row=3, column=0, columnspan=2, sticky="w", padx=5)

        input_frame.grid_columnconfigure(1, weight=1) # Hacer que la columna 1 se expanda

        # Botón de Iniciar Simulación
        self.start_button = tk.Button(config_frame, text="Iniciar Simulación", command=self._start_simulation_handler,
                                      bg='#4CAF50', fg='white', font=('Arial', 12, 'bold'), relief="raised", bd=3,
                                      activebackground='#45a049', activeforeground='white')
        self.start_button.pack(pady=10, fill="x")

        # --- Sección de Simulación Paso a Paso ---
        simulation_frame = tk.LabelFrame(self.root, text="Simulación Paso a Paso", padx=10, pady=10)
        simulation_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.simulation_steps_text = scrolledtext.ScrolledText(simulation_frame, width=70, height=10, wrap=tk.WORD,
                                                               font=('Consolas', 11), state='disabled', bd=2, relief="sunken",
                                                               bg='#f8f8f8', fg='#333333')
        self.simulation_steps_text.pack(pady=5, fill="both", expand=True)

        # Contenedor para opciones de elección
        self.choice_container = tk.Frame(simulation_frame, bd=2, relief="ridge", padx=10, pady=10)
        self.choice_container.pack(pady=5, fill="x")
        self.choice_container.pack_forget() # Ocultar inicialmente

        self.choice_label = tk.Label(self.choice_container, text="Seleccione una sustitución para [No-Terminal]:",
                                     font=('Arial', 10, 'bold'), fg='#333333')
        self.choice_label.pack(side="left", padx=(0, 10))

        self.choice_buttons_frame = tk.Frame(self.choice_container)
        self.choice_buttons_frame.pack(side="left", fill="x", expand=True)

        # Cuadro de Mensajes
        self.message_box = tk.Label(self.root, text="", font=('Arial', 10, 'bold'), wraplength=700, justify="center",
                                    pady=5, bd=1, relief="solid")
        self.message_box.pack(pady=5, padx=10, fill="x")
        self.message_box.pack_forget() # Ocultar inicialmente

        # Botón para Generar Árbol de Derivación
        self.generate_tree_button = tk.Button(self.root, text="Generar Árbol de Derivación", command=self._show_derivation_tree,
                                              bg='#007BFF', fg='white', font=('Arial', 12, 'bold'), relief="raised", bd=3,
                                              activebackground='#0056b3', activeforeground='white')
        self.generate_tree_button.pack(pady=10, padx=10, fill="x")
        self.generate_tree_button.config(state='disabled') # Deshabilitar inicialmente

    def _start_simulation_handler(self):
        """
        Manejador para el botón "Iniciar Simulación".
        Limpia la salida, reinicia el log de derivación y llama al simulador para iniciar.
        """
        self.simulation_steps_text.config(state='normal')
        self.simulation_steps_text.delete(1.0, END)
        self.simulation_steps_text.config(state='disabled')
        
        self.derivation_log = [] # Limpiar el log de derivación para una nueva simulación
        self.simulator.reset_simulation() # Resetear el estado del simulador
        
        rules = self.rules_input.get(1.0, END).strip()
        start_symbol = self.start_symbol_input.get().strip()
        target_string = self.target_string_input.get().strip()
        
        # Habilitar el botón de generar árbol una vez que la simulación ha comenzado
        self.generate_tree_button.config(state='normal')

        self.simulator.start_simulation(rules, start_symbol, target_string)

    def display_step(self, step, current_str, old_str='', idx=-1, prod=''):
        """
        Muestra un paso de la derivación en el área de texto y guarda los detalles del paso.
        Este es un callback para el simulador.

        Args:
            step (int): Número de paso.
            current_str (str): Cadena actual.
            old_str (str): Cadena antes de la sustitución (para resaltado).
            idx (int): Índice de la sustitución.
            prod (str): Producción utilizada.
        """
        # Guardar los detalles del paso para la construcción del árbol
        # El primer paso (step 0) es solo el símbolo inicial, no una sustitución
        if step == 0:
            self.derivation_log.append({
                'step': step,
                'current_string': current_str,
                'old_string': None, # No hay cadena anterior
                'non_terminal': current_str, # Símbolo inicial es el primer no-terminal
                'index_in_old': -1,
                'production': None,
            })
        else:
            self.derivation_log.append({
                'step': step,
                'current_string': current_str,
                'old_string': old_str,
                'non_terminal': old_str[idx] if idx != -1 else None, # El no-terminal que fue sustituido
                'index_in_old': idx,
                'production': prod,
            })

        self.simulation_steps_text.config(state='normal')
        
        step_text = f"Paso {step}: "
        if old_str and idx != -1:
            non_terminal_char = old_str[idx]
            # Resaltar el no-terminal sustituido con corchetes en la cadena anterior
            highlighted_old = old_str[:idx] + f"[{non_terminal_char}]" + old_str[idx+1:] 
            step_text += f"`{highlighted_old}` -> ({non_terminal_char} -> {prod}) -> `{current_str}`"
        else: # Para el paso inicial
            step_text += f"`{current_str}` (Símbolo Inicial)"
        
        self.simulation_steps_text.insert(END, step_text + "\n")
        self.simulation_steps_text.see(END) # Auto-scroll
        self.simulation_steps_text.config(state='disabled')

    def ask_for_choice(self, non_terminal, productions):
        """
        Muestra botones para que el usuario elija una producción.
        Este es un callback para el simulador.

        Args:
            non_terminal (str): El no-terminal a sustituir.
            productions (list): Lista de producciones posibles.
        """
        self.clear_choices_buttons() # Limpiar cualquier botón previo
        self.choice_label.config(text=f"Seleccione una sustitución para {non_terminal}:")
        self.choice_container.pack(pady=5, fill="x")

        for prod in productions:
            button_text = f"'{prod}'" if prod != 'ε' else "ε (cadena vacía)"
            button = tk.Button(self.choice_buttons_frame, text=button_text,
                               command=lambda p=prod: self.simulator.perform_step(p),
                               bg='#607D8B', fg='white', font=('Arial', 10), relief="raised", bd=2)
            button.pack(side="left", padx=2, pady=2)
            self.current_choice_buttons.append(button)

    def clear_choices_buttons(self):
        """
        Oculta el contenedor de opciones y elimina los botones de elección existentes.
        Este es un callback para el simulador.
        """
        for button in self.current_choice_buttons:
            button.destroy()
        self.current_choice_buttons = []
        self.choice_container.pack_forget()

    def display_message(self, message, message_type='info'):
        """
        Muestra un mensaje en el cuadro de mensajes de la UI.
        Este es un callback para el simulador.

        Args:
            message (str): El mensaje a mostrar.
            message_type (str): Tipo de mensaje ('success', 'error', 'info').
        """
        self.message_box.config(text=message)
        if message:
            self.message_box.pack(pady=5, padx=10, fill="x")
            if message_type == 'success':
                self.message_box.config(bg='#D4EDDA', fg='#155724', relief="solid", bd=1) # Verde claro
            elif message_type == 'error':
                self.message_box.config(bg='#F8D7DA', fg='#721C24', relief="solid", bd=1) # Rojo claro
            else: # info
                self.message_box.config(bg='#CCE5FF', fg='#004085', relief="solid", bd=1) # Azul claro
        else:
            self.message_box.pack_forget()

    def _show_derivation_tree(self):
        """
        Crea una nueva ventana (Toplevel) y dibuja el árbol de derivación en un Canvas.
        """
        if not self.derivation_log:
            messagebox.showinfo("Árbol de Derivación", "No hay derivación para generar un árbol. Inicie una simulación primero.")
            return

        tree_root_node = build_parse_tree(self.derivation_log)
        
        if not tree_root_node:
            messagebox.showinfo("Árbol de Derivación", "No se pudo construir el árbol de derivación a partir del log.")
            return

        tree_window = Toplevel(self.root)
        tree_window.title("Árbol de Derivación")
        tree_window.geometry("800x600") # Tamaño inicial para la ventana del árbol

        # Crear un Canvas para dibujar el árbol
        self.tree_canvas = Canvas(tree_window, bg='white', scrollregion=(0,0,1000,1000)) # Ajustar scrollregion si es necesario
        
        # Barras de desplazamiento
        hbar = tk.Scrollbar(tree_window, orient=tk.HORIZONTAL, command=self.tree_canvas.xview)
        vbar = tk.Scrollbar(tree_window, orient=tk.VERTICAL, command=self.tree_canvas.yview)
        self.tree_canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree_canvas.pack(expand=True, fill="both")

        self._draw_tree_on_canvas(self.tree_canvas, tree_root_node)


    def _draw_tree_on_canvas(self, canvas, root_node):
        """
        Dibuja el árbol de derivación en el canvas de Tkinter.
        Implementa un layout básico para el árbol.
        """
        if not root_node:
            return

        # Parámetros de diseño
        NODE_WIDTH = 60
        NODE_HEIGHT = 30
        X_SPACING = 30 # Espacio horizontal entre nodos
        Y_SPACING = 50 # Espacio vertical entre niveles

        # Diccionario para almacenar las coordenadas de cada nodo dibujado
        node_coords = {}
        # Diccionario para almacenar los nodos por nivel (para calcular el ancho de cada nivel)
        levels = {}

        # 1. Travesía BFS para organizar nodos por nivel y calcular sus dimensiones
        queue = [(root_node, 0)] # (node, depth)
        max_depth = 0
        while queue:
            current_node, depth = queue.pop(0)
            max_depth = max(max_depth, depth)

            if depth not in levels:
                levels[depth] = []
            levels[depth].append(current_node)

            for child in current_node.children:
                queue.append((child, depth + 1))

        # 2. Asignar posiciones X iniciales a los nodos.
        #    Una forma simple es asignar X basándose en el orden de aparición en el nivel.
        #    Luego ajustar X para centrar el nodo padre sobre sus hijos.
        
        # Para árboles más grandes, un algoritmo de posicionamiento más avanzado sería necesario.
        # Este es un enfoque simplificado:
        
        # Calcular el ancho total que necesitaría el nivel más ancho
        max_level_width = 0
        for depth in levels:
            level_width = len(levels[depth]) * (NODE_WIDTH + X_SPACING) - X_SPACING
            max_level_width = max(max_level_width, level_width)

        start_x_offset = max_level_width / 2 # Centro horizontal de la rama más ancha
        
        # Diccionario para mantener el seguimiento de la posición X actual en cada nivel
        current_x_per_level = {}

        # Recorrido para asignar coordenadas
        # Se podría usar un DFS para calcular mejor el ancho de sub-árboles y posicionar
        # a los padres sobre el centro de sus hijos. Para simplicidad, haremos un layout de arriba a abajo, izquierda a derecha.

        # DFS para calcular las coordenadas x de los nodos
        def calculate_node_positions(node, depth, x_offset):
            node.y = 50 + depth * (NODE_HEIGHT + Y_SPACING)
            
            if not node.children: # Es un nodo hoja
                # Asignar una posición x basada en el "next_x" para este nivel
                if depth not in current_x_per_level:
                    current_x_per_level[depth] = 50 # Start from a fixed left margin
                
                node.x = current_x_per_level[depth]
                current_x_per_level[depth] += NODE_WIDTH + X_SPACING
                node.width = NODE_WIDTH # Ancho base para hojas
                node_coords[node] = (node.x + NODE_WIDTH / 2, node.y + NODE_HEIGHT / 2) # Guardar centro
            else: # Es un nodo no-terminal con hijos
                children_x_coords = []
                for child in node.children:
                    # Recursivamente calcular la posición de los hijos
                    calculate_node_positions(child, depth + 1, x_offset)
                    children_x_coords.append(child.x)
                
                # Posicionar el nodo padre en el centro de sus hijos
                min_child_x = min(children_x_coords)
                max_child_x = max(children_x_coords)
                node.x = min_child_x + (max_child_x - min_child_x) / 2
                node.width = max_child_x - min_child_x + NODE_WIDTH # Ancho del sub-árbol

                node_coords[node] = (node.x + NODE_WIDTH / 2, node.y + NODE_HEIGHT / 2) # Guardar centro
        
        # Iniciar el cálculo de posiciones desde la raíz
        # Nota: este cálculo simple de x podría resultar en solapamientos para árboles complejos.
        # Para un layout perfecto, se necesitaría un algoritmo como Reingold-Tilford.
        calculate_node_positions(root_node, 0, start_x_offset)

        # 3. Dibujar nodos y aristas
        queue_draw = [root_node]
        drawn_nodes = set() # Para evitar dibujar el mismo nodo múltiples veces si hay referencias circulares (no debería pasar aquí)

        min_x = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')

        while queue_draw:
            current_node = queue_draw.pop(0)

            if current_node in drawn_nodes:
                continue
            drawn_nodes.add(current_node)

            # Dibujar el nodo
            center_x, center_y = current_node.x, current_node.y # Ya calculados
            
            # Ajustar para que x,y sean la esquina superior izquierda del óvalo/rectángulo
            oval_x1 = center_x - NODE_WIDTH / 2
            oval_y1 = center_y - NODE_HEIGHT / 2
            oval_x2 = center_x + NODE_WIDTH / 2
            oval_y2 = center_y + NODE_HEIGHT / 2

            node_color = 'lightblue'
            outline_color = 'blue'
            text_color = 'black'
            node_shape_type = 'oval' # Por defecto

            if current_node.is_terminal:
                node_color = 'lightgrey'
                outline_color = 'gray'
                node_shape_type = 'rectangle'
            elif current_node.symbol == 'epsilon':
                current_node.symbol = 'ε' # Mostrar epsilon
                node_color = 'white' # Sin fondo
                outline_color = 'white' # Sin borde
                text_color = 'gray'
                node_shape_type = 'text' # Solo texto

            if node_shape_type == 'oval':
                canvas.create_oval(oval_x1, oval_y1, oval_x2, oval_y2,
                                   fill=node_color, outline=outline_color, width=2)
            elif node_shape_type == 'rectangle':
                 canvas.create_rectangle(oval_x1, oval_y1, oval_x2, oval_y2,
                                         fill=node_color, outline=outline_color, width=2)
            # Para el texto, siempre se dibuja
            canvas.create_text(center_x, center_y, text=current_node.symbol,
                               font=('Arial', 12, 'bold'), fill=text_color)

            # Actualizar límites para el scrollregion
            min_x = min(min_x, oval_x1)
            max_x = max(max_x, oval_x2)
            max_y = max(max_y, oval_y2) # La y mínima siempre será 0 o un margen inicial

            # Dibujar aristas a los hijos
            for child in current_node.children:
                # La línea va del centro del padre al centro del hijo
                child_center_x, child_center_y = child.x, child.y
                
                # Para que las líneas no se solapen con los nodos
                # Calculamos puntos en el borde del óvalo/rectángulo
                # Simplificamos el cálculo del punto de conexión para evitar complejidad
                # simplemente conectando el centro inferior del padre al centro superior del hijo
                
                canvas.create_line(center_x, center_y + NODE_HEIGHT / 2, # Parte inferior del padre
                                   child_center_x, child_center_y - NODE_HEIGHT / 2, # Parte superior del hijo
                                   fill='black', width=1.5, arrow=tk.LAST)
                
                queue_draw.append(child)

        # Ajustar el scrollregion del canvas
        # Añadir un margen extra al scrollregion
        padding = 50
        canvas.config(scrollregion=(min_x - padding, 0, max_x + padding, max_y + padding))


if __name__ == "__main__":
    root = tk.Tk()
    app = CFGSimulatorApp(root)
    root.mainloop()

