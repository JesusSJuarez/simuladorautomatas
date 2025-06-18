import tkinter as tk
import math

class DerivationTree(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg='white', **kwargs)
        self.node_radius = 20
        self.level_height = 80
        self.horizontal_spacing = 40
        
        # Variables para el desplazamiento
        self.scroll_x = 0
        self.scroll_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        
        # Configurar eventos del mouse
        self.bind("<ButtonPress-1>", self.on_drag_start)
        self.bind("<B1-Motion>", self.on_drag_move)
        self.bind("<ButtonRelease-1>", self.on_drag_end)
        self.bind("<MouseWheel>", self.on_mousewheel)
        
    def on_drag_start(self, event):
        """Inicia el arrastre"""
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
    def on_drag_move(self, event):
        """Mueve el árbol durante el arrastre"""
        delta_x = event.x - self.drag_start_x
        delta_y = event.y - self.drag_start_y
        
        self.scroll_x += delta_x
        self.scroll_y += delta_y
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.redraw()
        
    def on_drag_end(self, event):
        """Finaliza el arrastre"""
        pass
        
    def on_mousewheel(self, event):
        """Zoom con la rueda del mouse"""
        zoom_factor = 1.1 if event.delta > 0 else 0.9
        
        # Ajustar el nivel de zoom
        self.level_height *= zoom_factor
        self.horizontal_spacing *= zoom_factor
        self.node_radius *= zoom_factor
        
        self.redraw()
        
    def redraw(self):
        """Redibuja el árbol con la posición actual"""
        self.delete("all")
        
        if not hasattr(self, 'current_history'):
            return
            
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Dibujar cada nivel
        for level, step in enumerate(self.current_history):
            y_pos = (level + 1) * self.level_height + self.scroll_y
            
            # Dibujar nodos en este nivel
            nodes = self._split_derivation(step['from'])
            for i, node in enumerate(nodes):
                x_pos = (width / (len(nodes) + 1)) * (i + 1) + self.scroll_x
                self._draw_node(x_pos, y_pos, node)
                
            # Dibujar flechas al siguiente nivel
            if level < len(self.current_history) - 1:
                next_nodes = self._split_derivation(self.current_history[level+1]['from'])
                for i, node in enumerate(next_nodes):
                    next_x = (width / (len(next_nodes) + 1)) * (i + 1) + self.scroll_x
                    next_y = (level + 2) * self.level_height + self.scroll_y
                    
                    # Conectar con el nodo padre correspondiente
                    parent_i = i % len(nodes)  # Simplificación - podría mejorarse
                    parent_x = (width / (len(nodes) + 1)) * (parent_i + 1) + self.scroll_x
                    parent_y = y_pos
                    
                    self.create_line(
                        next_x, next_y - self.node_radius,
                        parent_x, parent_y + self.node_radius,
                        arrow=tk.LAST, width=1
                    )
        
    def draw_step(self, step, history):
        """Dibuja un paso de la derivación"""
        self.current_history = history + [step]
        self.scroll_x = 0
        self.scroll_y = 0
        self.redraw()
        
    def _draw_node(self, x, y, text):
        """Dibuja un nodo del árbol"""
        self.create_oval(
            x - self.node_radius, y - self.node_radius,
            x + self.node_radius, y + self.node_radius,
            fill="lightblue", outline="black"
        )
        self.create_text(x, y, text=text, font=("Arial", 10))
        
    def _split_derivation(self, derivation):
        """Divide una cadena derivada en componentes para visualización"""
        return [c for c in derivation if c != ' ']
        
    def clear(self):
        """Limpia el canvas"""
        self.delete("all")
        if hasattr(self, 'current_history'):
            del self.current_history