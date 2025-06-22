# derivation_tree_generator.py

class ParseTreeNode:
    """
    Representa un nodo en el árbol de derivación.
    """
    def __init__(self, symbol, parent=None, is_terminal=False):
        self.symbol = symbol
        self.children = []
        self.parent = parent
        self.is_terminal = is_terminal
        # Atributos para el dibujo en Tkinter (se llenarán en gui_app.py)
        self.x = 0
        self.y = 0
        self.width = 0 # Ancho calculado para layout
        self.left_contour = 0 # Contorno izquierdo para layout
        self.right_contour = 0 # Contorno derecho para layout


    def add_child(self, child_node):
        """Añade un nodo hijo a este nodo."""
        self.children.append(child_node)

def build_parse_tree(derivation_log):
    """
    Construye un árbol de análisis sintáctico (parse tree) a partir de un log de derivación por la izquierda.

    Args:
        derivation_log (list): Una lista de diccionarios, donde cada diccionario
                                representa un paso de la derivación.
                                Ejemplo de diccionario de paso:
                                {'step': N, 'current_string': S_n, 'old_string': S_{n-1},
                                 'non_terminal': non_terminal_char,
                                 'index_in_old': index_of_non_terminal,
                                 'production': production_used}.

    Returns:
        ParseTreeNode: El nodo raíz del árbol de análisis, o None si el log está vacío.
    """
    if not derivation_log:
        return None

    start_symbol = derivation_log[0]['current_string']
    root = ParseTreeNode(start_symbol)

    # Cola de objetos ParseTreeNode (no-terminales) que aún no han sido expandidos,
    # en orden de derivación por la izquierda.
    active_nodes = [root] 

    # Iteramos a través de los pasos de la derivación, saltando el paso inicial 0
    # ya que es solo el símbolo de inicio.
    for i in range(1, len(derivation_log)):
        step_data = derivation_log[i]
        non_terminal_to_expand_symbol = step_data['non_terminal']
        production_used = step_data['production']

        if not active_nodes:
            print(f"Error: La cola de nodos activos está vacía en el paso {i}. No se puede expandir {non_terminal_to_expand_symbol}. Construcción del árbol abortada.")
            return None # No se puede construir un árbol consistente

        # El nodo a expandir es el no-terminal más a la izquierda sin expandir en nuestra estructura de árbol.
        # Quitamos el primer elemento de la cola.
        node_to_expand = active_nodes.pop(0)

        # Verificación de consistencia básica (aunque el simulador ya fuerza la derivación por la izquierda)
        if node_to_expand.symbol != non_terminal_to_expand_symbol:
            # Esto indica una inconsistencia entre el log y la expansión esperada por la izquierda en el árbol.
            # Se intenta encontrar el nodo correcto como respaldo, pero es una situación crítica.
            found = False
            for k, n in enumerate(active_nodes):
                if n.symbol == non_terminal_to_expand_symbol:
                    node_to_expand = active_nodes.pop(k)
                    found = True
                    break
            if not found:
                print(f"Crítico: No se pudo encontrar el nodo para expandir '{non_terminal_to_expand_symbol}' en la cola de nodos activos en el paso {i}. Abortando la construcción del árbol.")
                return None # No se puede construir un árbol consistente

        new_non_terminals_for_queue = []
        for char in production_used:
            is_terminal_char = not ('A' <= char <= 'Z' and len(char) == 1)
            child_node = ParseTreeNode(char if char != 'ε' else 'epsilon', node_to_expand, is_terminal_char)
            node_to_expand.add_child(child_node)
            if not is_terminal_char:
                new_non_terminals_for_queue.append(child_node)
        
        # Insertar los nuevos no-terminales al principio de la cola de active_nodes
        # porque esto corresponde a una derivación por la izquierda.
        active_nodes = new_non_terminals_for_queue + active_nodes

    return root

