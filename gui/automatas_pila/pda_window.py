import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.pda_simulator import PDASimulator
from core.pda_file_handler import PDAFileHandler
from gui.automatas_pila.pda_graph import PDAGraph
import os

class PDAWindow(tk.Toplevel):
    """
    Ventana principal de la aplicación para el Simulador de Autómatas de Pila.
    """
    def __init__(self, master):
        super().__init__(master)
        self.title("Simulador de Autómatas de Pila")
        self.geometry("1200x800") # Tamaño aumentado para acomodar la visualización de la pila

        self.simulator = PDASimulator()
        
        self.create_widgets()
        self.setup_layout()
        self.setup_event_bindings()
        
        self.input_string_index = 0 # Para rastrear la posición actual en la cadena de entrada

    def create_widgets(self):
        """Crea todos los widgets de la GUI."""
        # --- Panel de Control ---
        self.control_frame = ttk.LabelFrame(self, text="Control", padding=10)
        
        self.load_btn = ttk.Button(
            self.control_frame, 
            text="Cargar Autómata de Pila", 
            command=self.load_pda_from_file
        )

        self.save_btn = ttk.Button(
            self.control_frame, 
            text="Guardar Autómata de Pila", 
            command=self.save_pda_to_file
        )
        
        self.input_label = ttk.Label(self.control_frame, text="Cadena de entrada:")
        self.input_entry = ttk.Entry(self.control_frame, width=30)
        
        self.simulate_full_btn = ttk.Button(
            self.control_frame, 
            text="Simular Completo", 
            command=self.start_full_simulation
        )
        
        self.step_btn = ttk.Button(
            self.control_frame, 
            text="Paso a Paso", 
            command=self.step_simulation,
            state=tk.DISABLED # Deshabilitado al inicio
        )
        
        self.reset_btn = ttk.Button(
            self.control_frame, 
            text="Reiniciar", 
            command=self.reset_simulation,
            state=tk.DISABLED # Deshabilitado al inicio
        )
        
        # --- Panel de Información del Autómata ---
        self.info_frame = ttk.LabelFrame(self, text="Información del Autómata", padding=10)
        self.info_text = tk.Text(self.info_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        
        # --- Panel de Historial de Simulación ---
        self.sim_history_frame = ttk.LabelFrame(self, text="Historial de Simulación", padding=10)
        self.sim_history_text = tk.Text(self.sim_history_frame, state=tk.DISABLED, wrap=tk.WORD)
        self.sim_history_scrollbar = ttk.Scrollbar(self.sim_history_frame, command=self.sim_history_text.yview)
        self.sim_history_text.config(yscrollcommand=self.sim_history_scrollbar.set)

        # --- Panel de Visualización ---
        self.visual_frame = ttk.LabelFrame(self, text="Visualización del Autómata", padding=10)
        self.canvas = tk.Canvas(self.visual_frame, bg='white', width=700, height=400, bd=2, relief="sunken")
        self.pda_graph = PDAGraph(self.canvas)

        # --- Panel de Visualización de la Pila ---
        self.stack_frame = ttk.LabelFrame(self, text="Pila Actual", padding=10)
        self.stack_display_listbox = tk.Listbox(self.stack_frame, height=15, width=20, font=("Arial", 12))
        self.stack_scrollbar = ttk.Scrollbar(self.stack_frame, command=self.stack_display_listbox.yview)
        self.stack_display_listbox.config(yscrollcommand=self.stack_scrollbar.set)
        
        # --- Visualización de la Cadena de Entrada y Símbolo Actual ---
        self.input_display_frame = ttk.LabelFrame(self, text="Cadena de Entrada", padding=5)
        self.input_display_label = ttk.Label(self.input_display_frame, text="Cadena: ", font=("Arial", 10))
        self.current_symbol_label = ttk.Label(self.input_display_frame, text="Símbolo Actual: ", font=("Arial", 10, "bold"))
        self.remaining_input_label = ttk.Label(self.input_display_frame, text="Restante: ", font=("Arial", 10))


    def setup_layout(self):
        """Configura el diseño de los widgets usando grid."""
        # Configurar pesos de la cuadrícula para un diseño responsivo
        self.columnconfigure(0, weight=1) # Control e Info
        self.columnconfigure(1, weight=2) # Simulación Historial y Visual
        self.columnconfigure(2, weight=0) # Pila (ancho fijo)
        self.rowconfigure(1, weight=1) # Filas de Info/Historial
        self.rowconfigure(2, weight=2) # Fila de Visualización

        # Marco de control
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.input_entry.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.simulate_full_btn.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.step_btn.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        self.reset_btn.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        # Marco de visualización de entrada
        self.input_display_frame.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.input_display_frame.columnconfigure(0, weight=1)
        self.input_display_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.current_symbol_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.remaining_input_label.grid(row=2, column=0, sticky="w", padx=5, pady=2)

        # Marco de información
        self.info_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.info_frame.rowconfigure(0, weight=1)
        self.info_frame.columnconfigure(0, weight=1)
        self.info_text.grid(row=0, column=0, sticky="nsew")
        
        # Marco de historial de simulación
        self.sim_history_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.sim_history_frame.rowconfigure(0, weight=1)
        self.sim_history_frame.columnconfigure(0, weight=1)
        self.sim_history_text.grid(row=0, column=0, sticky="nsew")
        self.sim_history_scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Marco de visualización
        self.visual_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.visual_frame.rowconfigure(0, weight=1)
        self.visual_frame.columnconfigure(0, weight=1)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # Marco de la pila
        self.stack_frame.grid(row=0, column=2, rowspan=3, sticky="nsew", padx=5, pady=5)
        self.stack_frame.rowconfigure(0, weight=1)
        self.stack_frame.columnconfigure(0, weight=1)
        self.stack_display_listbox.grid(row=0, column=0, sticky="nsew")
        self.stack_scrollbar.grid(row=0, column=1, sticky="ns")

    def update_pda_info(self):
        """Actualiza la visualización de la información del AP."""
        self.info_text['state'] = tk.NORMAL
        self.info_text.delete(1.0, tk.END)
        
        if not self.simulator.pda:
            self.info_text.insert(tk.END, "No hay autómata de pila cargado.")
            self.info_text['state'] = tk.DISABLED
            return

        pda = self.simulator.pda
        info = f"Nombre: {getattr(pda, 'name', 'N/A')}\n" # Asumiendo que 'name' puede establecerse desde JSON
        info += f"Estados (Q): {', '.join(sorted(list(pda.states)))}\n"
        info += f"Alfabeto de Entrada (Σ): {', '.join(sorted(list(pda.input_alphabet)))}\n"
        info += f"Alfabeto de Pila (Γ): {', '.join(sorted(list(pda.stack_alphabet)))}\n"
        info += f"Estado Inicial (q0): {pda.initial_state}\n"
        info += f"Símbolo Inicial de Pila (Z0): {pda.initial_stack_symbol}\n"
        info += f"Estados Finales (F): {', '.join(sorted(list(pda.final_states)))}\n\n"
        info += "Transiciones (δ(q, a, Z) = (p, γ')):\n"
        
        # Ordenar transiciones para una visualización consistente
        sorted_transitions_keys = sorted(list(pda.transitions.keys()), key=lambda x: (x[0], x[1], x[2]))
        
        for (q, a, Z_top) in sorted_transitions_keys:
            targets = pda.transitions[(q, a, Z_top)]
            
            # Formatear símbolos de entrada/pila para la visualización ('ε' para cadena vacía)
            input_sym_display = a if a != '' else 'ε'
            stack_top_display = Z_top if Z_top != '' else 'ε'

            for next_q, push_symbols in targets:
                push_display = ''.join([s if s != '' else 'ε' for s in push_symbols])
                info += f"  δ({q}, {input_sym_display}, {stack_top_display}) = ({next_q}, {push_display})\n"
                
        self.info_text.insert(tk.END, info)
        self.info_text['state'] = tk.DISABLED
        
    def draw_pda_graph(self):
        """Dibuja el grafo del AP en el lienzo."""
        if self.simulator.pda:
            self.pda_graph.draw_pda(
                states=list(self.simulator.pda.states),
                transitions=self.simulator.pda.transitions,
                initial_state=self.simulator.pda.initial_state,
                final_states=list(self.simulator.pda.final_states)
            )
            initial_state = self.simulator.pda.initial_state
            self.pda_graph.highlight_states({initial_state})
        else:
            self.canvas.delete("all") # Limpiar el lienzo si no hay AP cargado

    def start_full_simulation(self):
        """Inicia una simulación completa de la cadena de entrada."""
        input_str = self.input_entry.get()
        if not input_str and not (self.simulator.pda and self.simulator.pda.is_accepted() and self.simulator.pda.current_configurations):
            if not input_str:
                messagebox.showerror("Error", "Por favor, ingrese una cadena de entrada para simular.")
            elif not self.simulator.pda:
                messagebox.showerror("Error", "Por favor, cargue un autómata de pila primero.")
            return
            
        self.simulator.set_input_string(input_str)
        self.simulator.simulate_full_string()
        self.display_simulation_history()
        self.update_stack_display()
        self.highlight_current_states()
        self.update_input_display()

        result_message = "Cadena Aceptada" if self.simulator.is_simulation_accepted() else "Cadena Rechazada"
        messagebox.showinfo("Simulación Completa", result_message)
        self.step_btn['state'] = tk.DISABLED # Deshabilitar el paso después de la simulación completa
        self.reset_btn['state'] = tk.NORMAL
        
    def step_simulation(self):
        """Realiza un paso de la simulación."""
        input_str = self.input_entry.get()
        if not input_str and not (self.simulator.pda and self.simulator.pda.is_accepted() and self.simulator.pda.current_configurations):
            if not input_str:
                messagebox.showerror("Error", "Por favor, ingrese una cadena de entrada para simular.")
            elif not self.simulator.pda:
                messagebox.showerror("Error", "Por favor, cargue un autómata de pila primero.")
            return

        # Si es el primer paso o si el input_string ha cambiado, reiniciar y establecer el input
        if not self.simulator.simulation_history and self.simulator.current_step_index == 0 or \
           self.simulator.input_string != input_str:
            self.simulator.set_input_string(input_str)
            # reset_simulation() ya se llama dentro de set_input_string()

        # Si la simulación ya terminó, no permitir más pasos.
        if self.simulator.is_finished:
            messagebox.showinfo("Fin de la Simulación", "La simulación ha terminado o el autómata está atascado.")
            self.step_btn['state'] = tk.DISABLED
            return
        
        performed_step = self.simulator.step_simulation()
        
        if not performed_step and self.simulator.is_finished:
            # Esto significa que no hubo más movimientos posibles Y ya se marcó como finalizado.
            messagebox.showinfo("Fin de la Simulación", "No hay más pasos posibles.")
            self.step_btn['state'] = tk.DISABLED
            return

        self.display_simulation_history()
        self.update_stack_display()
        self.highlight_current_states()
        self.update_input_display()

        if self.simulator.is_finished:
            result_message = "Cadena Aceptada" if self.simulator.is_simulation_accepted() else "Cadena Rechazada"
            messagebox.showinfo("Simulación Completa", result_message)
            self.step_btn['state'] = tk.DISABLED
            
        self.reset_btn['state'] = tk.NORMAL # Habilitar reset siempre que haya un autómata cargado

    def reset_simulation(self):
        """Reinicia la simulación y GUI displays."""
        if not self.simulator.pda: # Si no hay autómata, no hay nada que resetear
            return
            
        self.simulator.reset_simulation()
        self.sim_history_text['state'] = tk.NORMAL
        self.sim_history_text.delete(1.0, tk.END)
        self.sim_history_text['state'] = tk.DISABLED
        
        self.stack_display_listbox.delete(0, tk.END)
        
        self.pda_graph.clear_highlights()
        if self.simulator.pda:
            initial_state = self.simulator.pda.initial_state
            self.pda_graph.highlight_states({initial_state})
            # Mostrar la pila inicial después de resetear (ya se hará con update_stack_display)
        
        self.display_simulation_history() # Mostrar el historial inicial (Inicio + epsilon-cierre)
        self.update_stack_display() # Mostrar la pila inicial
        self.update_input_display() # Reiniciar visualización de entrada

        # Habilitar o deshabilitar botones basado en el estado del autómata y la entrada
        self.step_btn['state'] = tk.NORMAL if self.simulator.pda and self.input_entry.get() else tk.DISABLED
        self.simulate_full_btn['state'] = tk.NORMAL if self.simulator.pda and self.input_entry.get() else tk.DISABLED
        self.reset_btn['state'] = tk.NORMAL if self.simulator.pda else tk.DISABLED


    def display_simulation_history(self):
        """Muestra el historial detallado de la simulación."""
        self.sim_history_text['state'] = tk.NORMAL
        self.sim_history_text.delete(1.0, tk.END)

        for i, step_info in enumerate(self.simulator.simulation_history):
            self.sim_history_text.insert(tk.END, f"--- Paso {i + 1} ---\n")
            self.sim_history_text.insert(tk.END, f"  Símbolo de entrada: '{step_info['input_symbol'] if step_info['input_symbol'] != '' else 'ε'}'\n")

            self.sim_history_text.insert(tk.END, "  Configuraciones antes:\n")
            if step_info['configurations_before']:
                for q, s in step_info['configurations_before']:
                    self.sim_history_text.insert(tk.END, f"    ({q}, Pila: {''.join(s) if s else 'ε'})\n")
            else:
                self.sim_history_text.insert(tk.END, "    Ninguna (inicio o atascado)\n")


            self.sim_history_text.insert(tk.END, "  Transiciones usadas:\n")
            if step_info['transitions_used']:
                for t in step_info['transitions_used']:
                    input_sym_display = t['input_symbol'] if t['input_symbol'] != '' else 'ε'
                    stack_pop_display = t['stack_pop_symbol'] if t['stack_pop_symbol'] != '' else 'ε'
                    stack_push_display = ''.join([s if s != '' else 'ε' for s in t['stack_push_symbols']])
                    self.sim_history_text.insert(tk.END,
                        f"    δ({t['from_state']}, {input_sym_display}, {stack_pop_display}) -> ({t['to_state']}, {stack_push_display})\n"
                    )
                    self.sim_history_text.insert(tk.END, f"      Pila antes: {''.join(t['from_stack']) if t['from_stack'] else 'ε'}\n")
                    self.sim_history_text.insert(tk.END, f"      Pila después: {''.join(t['to_stack']) if t['to_stack'] else 'ε'}\n")
            else:
                self.sim_history_text.insert(tk.END, "    Ninguna transición válida o autómata atascado.\n")

            self.sim_history_text.insert(tk.END, "  Configuraciones después:\n")
            if step_info['configurations_after']:
                for q, s in step_info['configurations_after']:
                    self.sim_history_text.insert(tk.END, f"    ({q}, Pila: {''.join(s) if s else 'ε'})\n")
            else:
                self.sim_history_text.insert(tk.END, "    Ninguna (autómata atascado)\n")

            self.sim_history_text.insert(tk.END, f"  Aceptación hasta este punto: {'Sí' if step_info['is_accepted'] else 'No'}\n\n")
            
        self.sim_history_text['state'] = tk.DISABLED
        self.sim_history_text.see(tk.END) # Desplazarse hasta el final

    def update_stack_display(self):
        """Actualiza la visualización de la pila con el/los contenido(s) de la pila actual(es)."""
        self.stack_display_listbox.delete(0, tk.END) # Limpiar la pila anterior
        
        current_stacks = self.simulator.get_current_stack_for_display()
        
        if not current_stacks or all(not stack for stack in current_stacks): # Si todas las pilas están vacías
            self.stack_display_listbox.insert(tk.END, "Pila Vacía (ε)")
        else:
            # Mostrar todas las posibles pilas para AP no deterministas
            for i, stack in enumerate(current_stacks):
                if stack:
                    # Mostrar pila de abajo hacia arriba (más fácil de leer)
                    self.stack_display_listbox.insert(tk.END, f"--- Pila {i+1} ---")
                    for j, symbol in enumerate(reversed(stack)):
                        if j == 0: # Cima de la pila
                            self.stack_display_listbox.insert(tk.END, f"-> {symbol} (cima)")
                        else:
                            self.stack_display_listbox.insert(tk.END, f"   {symbol}")
                else: # Una de las posibles pilas está vacía
                    self.stack_display_listbox.insert(tk.END, f"--- Pila {i+1} ---")
                    self.stack_display_listbox.insert(tk.END, "Pila Vacía (ε)")
                
                if i < len(current_stacks) - 1: # Añadir separador si hay más pilas
                    self.stack_display_listbox.insert(tk.END, "") # Línea en blanco entre pilas
        self.stack_display_listbox.see(tk.END) # Desplazarse hasta el final


    def highlight_current_states(self):
        """Resalta los estados actuales en el grafo del AP."""
        current_states = self.simulator.get_current_states_for_display()
        self.pda_graph.highlight_states(current_states)
        
    def update_input_display(self):
        """Actualiza la visualización de la cadena de entrada y el símbolo actual."""
        full_input = self.input_entry.get() # Tomar siempre la cadena completa del entry
        remaining_input = self.simulator.get_remaining_input()
        current_symbol_display = self.simulator.get_current_input_symbol()
        
        self.input_display_label.config(text=f"Cadena Completa: '{full_input}'")
        self.current_symbol_label.config(text=f"Símbolo Actual: '{current_symbol_display}'")
        self.remaining_input_label.config(text=f"Cadena Restante: '{remaining_input if remaining_input else 'ε'}'")


    def setup_event_bindings(self):
        """Configura los enlaces de eventos para un comportamiento responsivo."""
        self.visual_frame.bind("<Configure>", self.on_canvas_resize)
        # Observar cambios en el campo de entrada para habilitar/deshabilitar botones
        self.input_entry.bind("<KeyRelease>", self.on_input_entry_change)
    
    def on_canvas_resize(self, event):
        """Redibuja el AP cuando cambia el tamaño del lienzo."""
        if hasattr(self, 'pda_graph') and self.simulator.pda:
            self.pda_graph.update_canvas_size(event.width, event.height)
            self.draw_pda_graph()
            self.highlight_current_states() # Volver a aplicar los resaltados después de redibujar

    def on_input_entry_change(self, event=None):
        """Habilita/deshabilita los botones de simulación basándose en la cadena de entrada."""
        has_input = bool(self.input_entry.get())
        has_pda = self.simulator.pda is not None
        
        self.step_btn['state'] = tk.NORMAL if has_input and has_pda else tk.DISABLED
        self.simulate_full_btn['state'] = tk.NORMAL if has_input and has_pda else tk.DISABLED
        self.reset_btn['state'] = tk.NORMAL if has_pda else tk.DISABLED # Reset puede ser usado sin input


    def load_pda_from_file(self):
        """Abre un diálogo para cargar un AP desde un JSON file."""
        file_path = filedialog.askopenfilename(
            title="Cargar Autómata de Pila",
            initialdir=os.path.join(os.path.dirname(__file__), "..", "examples"), # Asumiendo la carpeta 'examples'
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                pda = PDAFileHandler.load_pda_from_file(file_path)
                self.simulator.load_pda(pda)
                pda.name = os.path.splitext(os.path.basename(file_path))[0]
                self.update_pda_info()
                self.draw_pda_graph()
                self.reset_simulation() # Resetear simulación y actualizar display
                self.title(f"Simulador de Autómatas de Pila - {os.path.basename(file_path)}")
                self.on_input_entry_change() # Re-evaluar estado de botones
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el autómata de pila:\n{str(e)}")

    def save_pda_to_file(self):
        """Abre un diálogo para guardar el AP actual en un JSON file."""
        if not self.simulator.pda:
            messagebox.showerror("Error", "No hay autómata de pila cargado para guardar.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar Autómata de Pila",
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                name = os.path.splitext(os.path.basename(file_path))[0]
                PDAFileHandler.save_pda_to_file(self.simulator.pda, file_path, name)
                messagebox.showinfo("Éxito", "Autómata de pila guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el autómata de pila:\n{str(e)}")
