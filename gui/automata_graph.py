import tkinter as tk
import math
from typing import Dict, List, Tuple, Set
from collections import defaultdict

class AutomataGraph:
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.node_radius = 30
        self.arrow_size = 10
        self.state_positions = {}
        self.transition_arcs = {}
        self.highlighted_states = set()
        
    def calculate_layout(self, states: List[str], transitions: Dict, initial_state: str, final_states: List[str]):
        """Calcula posiciones para los nodos usando algoritmo circular"""
        self.state_positions = {}
        center_x = self.canvas.winfo_width() / 2
        center_y = self.canvas.winfo_height() / 2
        radius = min(center_x, center_y) * 0.7
        
        angle_step = 2 * math.pi / len(states)
        for i, state in enumerate(states):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.state_positions[state] = (x, y)
            
    def draw_automata(self, states: List[str], transitions: Dict, initial_state: str, final_states: List[str]):
        """Dibuja todo el autómata en el canvas"""
        self.canvas.delete("all")
        self.calculate_layout(states, transitions, initial_state, final_states)
        self._draw_transitions(transitions)
        
        for state, pos in self.state_positions.items():
            self._draw_state(state, pos, state in final_states)
            
        if initial_state in self.state_positions:
            self._draw_initial_marker(initial_state)
        
        
    def _optimize_layout(self, transitions: Dict):
        """Mejora el layout basado en la frecuencia de transiciones"""
        # Implementación básica - podrías usar un algoritmo más sofisticado como force-directed
        pass
        
                
    def _draw_state(self, state: str, pos: Tuple[float, float], is_final: bool):
        """Dibuja un estado individual"""
        x, y = pos
        fill_color = "lightblue"  # Color normal
        if state in self.highlighted_states:
            fill_color = "#90EE90"  # Verde claro para estado inicial
        # Estado normal
        self.canvas.create_oval(
            x - self.node_radius, y - self.node_radius,
            x + self.node_radius, y + self.node_radius,
            fill=fill_color, outline="black", width=2,
            tags=("state", f"state_{state}"))
        # Estado final (doble círculo)
        if is_final:
            self.canvas.create_oval(
                x - self.node_radius - 5, y - self.node_radius - 5,
                x + self.node_radius + 5, y + self.node_radius + 5,
                outline="black", width=2,
                tags=("state", f"state_{state}", "final_state"))
                
        # Etiqueta del estado
        self.canvas.create_text(
            x, y, text=state, font=("Arial", 10),
            tags=("state_label", f"label_{state}"))
            
    def _draw_initial_marker(self, initial_state: str):
        """Dibuja la flecha que indica el estado inicial"""
        x, y = self.state_positions[initial_state]
        start_x = x - self.node_radius - 30
        start_y = y
        
        self.canvas.create_line(
            start_x, start_y,
            x - self.node_radius, y,
            arrow=tk.LAST, width=2,
            tags=("initial_marker", f"marker_{initial_state}"))
            
    def _draw_transitions(self, transitions: Dict):
        """Dibuja todas las transiciones"""
        self.transition_arcs = defaultdict(list)
        
        for from_state, trans in transitions.items():
            for symbol, to_states in trans.items():
                for to_state in to_states:
                    if from_state in self.state_positions and to_state in self.state_positions:
                        if from_state == to_state:
                            # Transición a sí mismo (loop)
                            self._draw_self_loop(from_state, symbol)
                        else:
                            # Transición normal
                            self._draw_normal_transition(from_state, to_state, symbol)
                            
    def _draw_normal_transition(self, from_state: str, to_state: str, symbol: str):
        """Dibuja una transición entre dos estados diferentes"""
        x1, y1 = self.state_positions[from_state]
        x2, y2 = self.state_positions[to_state]
        
        # Calcular ángulo entre nodos
        dx = x2 - x1
        dy = y2 - y1
        angle = math.atan2(dy, dx)
        
        # Puntos de inicio y fin (en el borde de los círculos)
        start_x = x1 + self.node_radius * math.cos(angle)
        start_y = y1 + self.node_radius * math.sin(angle)
        end_x = x2 - self.node_radius * math.cos(angle)
        end_y = y2 - self.node_radius * math.sin(angle)
        
        # Crear la flecha
        arrow = self.canvas.create_line(
            start_x, start_y, end_x, end_y,
            arrow=tk.LAST, width=1.5,
            tags=("transition", f"trans_{from_state}_{to_state}_{symbol}"))
            
        # Posicionar la etiqueta
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Ajustar posición para evitar superposición
        label_x = mid_x + 10 * math.cos(angle + math.pi/2)
        label_y = mid_y + 10 * math.sin(angle + math.pi/2)
        
        self.canvas.create_text(
            label_x, label_y, text=symbol, font=("Arial", 8),
            tags=("transition_label", f"trans_label_{from_state}_{to_state}_{symbol}"))
            
        self.transition_arcs[(from_state, to_state)].append((arrow, symbol))
        
    def _draw_self_loop(self, state: str, symbol: str):
        """Dibuja una transición que vuelve al mismo estado"""
        x, y = self.state_positions[state]
        loop_radius = self.node_radius * 1.5
        
        # Crear arco circular
        loop = self.canvas.create_arc(
            x - loop_radius, y - loop_radius,
            x + loop_radius, y + loop_radius,
            start=45, extent=270, style=tk.ARC,
            width=1.5, tags=("transition", f"trans_{state}_self_{symbol}"))
            
        # Flecha al final del arco
        arrow_angle = math.radians(45 + 270 - 10)  # 10 grados antes del final
        arrow_x = x + loop_radius * math.cos(arrow_angle)
        arrow_y = y + loop_radius * math.sin(arrow_angle)
        
        # Pequeña línea para la flecha
        arrow_end_x = x + loop_radius * math.cos(math.radians(45 + 270))
        arrow_end_y = y + loop_radius * math.sin(math.radians(45 + 270))
        
        self.canvas.create_line(
            arrow_x, arrow_y, arrow_end_x, arrow_end_y,
            arrow=tk.LAST, width=1.5,
            tags=("transition_arrow", f"trans_arrow_{state}_self_{symbol}"))
            
        # Etiqueta del loop
        label_angle = math.radians(180)
        label_x = x + (loop_radius + 10) * math.cos(label_angle)
        label_y = y + (loop_radius + 10) * math.sin(label_angle)
        
        self.canvas.create_text(
            label_x, label_y, text=symbol, font=("Arial", 8),
            tags=("transition_label", f"trans_label_{state}_self_{symbol}"))
            
        self.transition_arcs[(state, state)].append((loop, symbol))
        
    def highlight_states(self, states: Set[str]):
        """Resalta los estados especificados"""
        # Quitar resaltado anterior
        self.canvas.delete("highlight")
        self.highlighted_states = set(states)
        
        # Aplicar nuevo resaltado
        for state in states:
            if state in self.state_positions:
                x, y = self.state_positions[state]
                color = "red"  # Color para estados durante simulación
                if state == list(self.state_positions.keys())[0]:  # Si es estado inicial
                    color = "#90EE90"  # Verde claro
                self.canvas.create_oval(
                    x - self.node_radius - 3, y - self.node_radius - 3,
                    x + self.node_radius + 3, y + self.node_radius + 3,
                    outline="red", width=3, tags="highlight")
                    
    def clear_highlights(self):
        """Elimina todos los resaltados"""
        self.canvas.delete("highlight")
        self.highlighted_states = set()
        
    def update_canvas_size(self, width: int, height: int):
        """Actualiza el tamaño del canvas y redibuja"""
        self.canvas.config(width=width, height=height)