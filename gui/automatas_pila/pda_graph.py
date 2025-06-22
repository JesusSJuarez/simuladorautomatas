import tkinter as tk
import math
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class PDAGraph:
    """
    Gestiona el dibujo del grafo del Autómata de Pila en un lienzo de Tkinter.
    """
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.node_radius = 30
        self.arrow_size = 10
        self.state_positions = {} # Almacena (x, y) para cada estado
        self.transition_arcs = defaultdict(list) # Almacena (id_linea, id_etiqueta) para cada clave de transición
        self.highlighted_states = set()

    def calculate_layout(self, states: List[str]):
        """Calcula las posiciones óptimas para los nodos usando un algoritmo circular."""
        self.state_positions = {}
        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2
        
        # Asegurar un radio mínimo para un número pequeño de estados
        radius = min(center_x, center_y) * 0.7
        if len(states) == 1:
            radius = 0 # Estado único centrado
        elif len(states) == 0:
            return

        # Posicionamiento circular para los estados
        angle_step = 2 * math.pi / len(states)
        for i, state in enumerate(states):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.state_positions[state] = (x, y)
            
    def draw_pda(self, states: List[str], transitions: Dict, initial_state: str, final_states: List[str]):
        """Dibuja todo el AP en el lienzo."""
        self.canvas.delete("all") # Borrar dibujo anterior
        self.calculate_layout(states)
        
        # Dibujar transiciones primero (para que queden detrás de los nodos)
        self._draw_transitions(transitions)
        
        # Dibujar los estados
        for state, pos in self.state_positions.items():
            self._draw_state(state, pos, state in final_states)
            
        # Dibujar marcador de estado inicial
        if initial_state in self.state_positions:
            self._draw_initial_marker(initial_state)
            
        # Volver a aplicar los resaltados si algún estado estaba resaltado antes de redibujar
        self.highlight_states(self.highlighted_states)
                
    def _draw_state(self, state: str, pos: Tuple[float, float], is_final: bool):
        """Dibuja un estado individual."""
        x, y = pos
        fill_color = "lightblue" # Color normal
        
        # Dibujar el círculo principal para el estado
        self.canvas.create_oval(
            x - self.node_radius, y - self.node_radius,
            x + self.node_radius, y + self.node_radius,
            fill=fill_color, outline="black", width=2,
            tags=("state", f"state_{state}"))
        
        # Dibujar el círculo interior para los estados finales
        if is_final:
            self.canvas.create_oval(
                x - self.node_radius + 5, y - self.node_radius + 5,
                x + self.node_radius - 5, y + self.node_radius - 5,
                outline="black", width=2,
                tags=("state", f"state_{state}", "final_state"))
                
        # Etiqueta del estado
        self.canvas.create_text(
            x, y, text=state, font=("Arial", 10, "bold"),
            tags=("state_label", f"label_{state}"))
            
    def _draw_initial_marker(self, initial_state: str):
        """Dibuja la flecha que indica el estado inicial."""
        x, y = self.state_positions[initial_state]
        start_x = x - self.node_radius - 30
        start_y = y
        
        self.canvas.create_line(
            start_x, start_y,
            x - self.node_radius, y,
            arrow=tk.LAST, width=2,
            tags=("initial_marker", f"marker_{initial_state}"))
            
    def _draw_transitions(self, transitions: Dict):
        """Dibuja todas las transiciones."""
        self.transition_arcs = defaultdict(list)
        
        # Agrupar transiciones entre los mismos dos estados para dibujarlas curvas o paralelas
        grouped_transitions = defaultdict(list) # Clave: (estado_origen, estado_destino), Valor: lista de (entrada, desapilar, apilar)
        for (from_state, input_sym, stack_top), targets in transitions.items():
            for to_state, push_symbols in targets:
                # Crear una representación estandarizada para la etiqueta
                label_text = f"{input_sym if input_sym != '' else 'ε'},{stack_top if stack_top != '' else 'ε'}/{''.join(push_symbols) if push_symbols != ('',) else 'ε'}"
                grouped_transitions[(from_state, to_state)].append(label_text)

        for (from_state, to_state), labels in grouped_transitions.items():
            if from_state == to_state:
                # Transiciones de bucle a sí mismo
                self._draw_self_loop(from_state, ", ".join(labels))
            else:
                # Transiciones normales o paralelas
                self._draw_normal_transition(from_state, to_state, ", ".join(labels))
                            
    def _draw_normal_transition(self, from_state: str, to_state: str, label: str):
        """Dibuja una transición entre dos estados diferentes."""
        x1, y1 = self.state_positions[from_state]
        x2, y2 = self.state_positions[to_state]
        
        # Calcular el ángulo para los puntos de conexión en los círculos
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)
        
        start_x = x1 + self.node_radius * math.cos(angle)
        start_y = y1 + self.node_radius * math.sin(angle)
        end_x = x2 - self.node_radius * math.cos(angle)
        end_y = y2 - self.node_radius * math.sin(angle)
        
        # Dibujar la línea de la flecha
        arrow = self.canvas.create_line(
            start_x, start_y, end_x, end_y,
            arrow=tk.LAST, width=1.5,
            tags=("transition", f"trans_{from_state}_{to_state}"))
            
        # Posicionar la etiqueta
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Desplazar la etiqueta para evitar superponerse a la línea
        label_offset = 15 # Distancia desde la línea
        label_x = mid_x + label_offset * math.cos(angle + math.pi/2)
        label_y = mid_y + label_offset * math.sin(angle + math.pi/2)
        
        text_id = self.canvas.create_text(
            label_x, label_y, text=label, font=("Arial", 8),
            tags=("transition_label", f"trans_label_{from_state}_{to_state}"))
            
        self.transition_arcs[(from_state, to_state)].append((arrow, text_id))
        
    def _draw_self_loop(self, state: str, label: str):
        """Dibuja una transición que regresa al mismo estado."""
        x, y = self.state_positions[state]
        loop_radius = self.node_radius * 1.5
        
        # Crear un arco circular (parte superior de un círculo)
        loop = self.canvas.create_arc(
            x - loop_radius, y - loop_radius,
            x + loop_radius, y + loop_radius,
            start=45, extent=270, style=tk.ARC, # Ajustado para dibujar un bucle más claro
            width=1.5, tags=("transition", f"trans_{state}_self"))
            
        # Dibujar la punta de flecha al final del arco
        # Calcular el punto en el arco donde debe estar la flecha
        arrow_angle_rad = math.radians(45 + 270) # Final del arco
        arrow_x = x + loop_radius * math.cos(arrow_angle_rad)
        arrow_y = y + loop_radius * math.sin(arrow_angle_rad)

        # Calcular un punto ligeramente antes del final para el inicio de la línea de la flecha
        # Usar una pequeña extensión para dibujar la flecha
        arrow_start_angle_rad = math.radians(45 + 270 - 10) # 10 grados antes del final
        arrow_start_x = x + loop_radius * math.cos(arrow_start_angle_rad)
        arrow_start_y = y + loop_radius * math.sin(arrow_start_angle_rad)

        self.canvas.create_line(
            arrow_start_x, arrow_start_y, arrow_x, arrow_y,
            arrow=tk.LAST, width=1.5,
            tags=("transition_arrow", f"trans_arrow_{state}_self"))
            
        # Posicionar la etiqueta para el bucle
        label_angle = math.radians(90) # Posicionar la etiqueta sobre el bucle
        label_x = x + (loop_radius) * math.cos(label_angle)
        label_y = y + (loop_radius) * math.sin(label_angle) - 15 # Ajustar verticalmente
        
        text_id = self.canvas.create_text(
            label_x, label_y, text=label, font=("Arial", 8),
            tags=("transition_label", f"trans_label_{state}_self"))
            
        self.transition_arcs[(state, state)].append((loop, text_id))
        
    def highlight_states(self, states: Set[str]):
        """Resalta los estados especificados."""
        self.canvas.delete("highlight") # Borrar resaltados anteriores
        self.highlighted_states = set(states) # Almacenar estados resaltados actuales
        
        # Aplicar nuevos resaltados
        for state in states:
            if state in self.state_positions:
                x, y = self.state_positions[state]
                
                # Dibujar un contorno más grueso para los estados resaltados
                self.canvas.create_oval(
                    x - self.node_radius - 3, y - self.node_radius - 3,
                    x + self.node_radius + 3, y + self.node_radius + 3,
                    outline="blue", width=3, tags="highlight")
                    
    def clear_highlights(self):
        """Elimina todos los resaltados."""
        self.canvas.delete("highlight")
        self.highlighted_states = set()
        
    def update_canvas_size(self, width: int, height: int):
        """Actualiza el tamaño del lienzo."""
        self.canvas.config(width=width, height=height)
