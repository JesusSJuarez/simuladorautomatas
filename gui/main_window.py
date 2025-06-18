import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.automata import Automata
from core.simulator import AutomataSimulator
from core.file_handler import FileHandler
from .automata_graph import AutomataGraph
from .grammar_window import GrammarWindow
import os

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Autómatas y Gramáticas")
        self.geometry("1000x700")
        self.simulator = AutomataSimulator()
        
        self.create_widgets()
        self.setup_layout()
        self.setup_event_bindings()
        self.setup_menu()
        
    def setup_menu(self):
        menubar = tk.Menu(self)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Cargar Autómata", command=self.load_automata_from_file)
        file_menu.add_command(label="Guardar Autómata", command=self.save_automata_to_file)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        
        # Menú Gramáticas
        grammar_menu = tk.Menu(menubar, tearoff=0)
        grammar_menu.add_command(label="Simular Gramática", command=self.open_grammar_window)
        menubar.add_cascade(label="Gramáticas", menu=grammar_menu)
        
        self.config(menu=menubar)
        
    def open_grammar_window(self):
        """Abre la ventana de simulación de gramáticas"""
        grammar_window = GrammarWindow(self)
        grammar_window.grab_set()
        
    def create_widgets(self):
        # Panel de control
        self.control_frame = ttk.LabelFrame(self, text="Control", padding=10)
        
        self.load_btn = ttk.Button(
            self.control_frame, 
            text="Cargar Autómata", 
            command=self.load_automata_from_file
        )

        self.save_btn = ttk.Button(
            self.control_frame, 
            text="Guardar Autómata", 
            command=self.save_automata_to_file
        )
        
        self.input_label = ttk.Label(self.control_frame, text="Cadena de entrada:")
        self.input_entry = ttk.Entry(self.control_frame, width=30)
        
        self.simulate_btn = ttk.Button(
            self.control_frame, 
            text="Simular", 
            command=self.start_simulation
        )
        
        self.step_btn = ttk.Button(
            self.control_frame, 
            text="Paso a Paso", 
            command=self.step_simulation,
            state=tk.DISABLED
        )
        
        self.reset_btn = ttk.Button(
            self.control_frame, 
            text="Reiniciar", 
            command=self.reset_simulation,
            state=tk.DISABLED
        )
        
        # Panel de información del autómata
        self.info_frame = ttk.LabelFrame(self, text="Información del Autómata", padding=10)
        self.info_text = tk.Text(self.info_frame, height=10, state=tk.DISABLED)
        
        # Panel de simulación
        self.sim_frame = ttk.LabelFrame(self, text="Simulación", padding=10)
        self.sim_text = tk.Text(self.sim_frame, height=15, state=tk.DISABLED)
        
        # Panel de visualización
        self.visual_frame = ttk.LabelFrame(self, text="Visualización", padding=10)
        self.canvas = tk.Canvas(self.visual_frame, bg='white', width=600, height=300)
        self.automata_graph = AutomataGraph(self.canvas)
        
    def setup_layout(self):
        # Configuración de grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        
        # Control frame
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.input_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.simulate_btn.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.step_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.reset_btn.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        
        # Info frame
        self.info_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.info_text.pack(expand=True, fill=tk.BOTH)
        
        # Sim frame
        self.sim_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        self.sim_text.pack(expand=True, fill=tk.BOTH)
        
        # Visual frame
        self.visual_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        
    def load_automata(self):
        # Aquí implementarías la carga de un autómata desde archivo
        # Por ahora creamos uno de ejemplo
        example_automata = Automata(
            states=['q0', 'q1', 'q2'],
            alphabet=['a', 'b'],
            transitions={
                'q0': {'a': ['q1'], 'b': ['q0']},
                'q1': {'a': ['q1'], 'b': ['q2']},
                'q2': {'a': ['q2'], 'b': ['q2']}
            },
            initial_state='q0',
            final_states=['q2']
        )
        
        self.simulator.load_automata(example_automata)
        self.update_automata_info()
        self.draw_automata()
        self.step_btn['state'] = tk.NORMAL
        self.reset_btn['state'] = tk.NORMAL
        
    def update_automata_info(self):
        self.info_text['state'] = tk.NORMAL
        self.info_text.delete(1.0, tk.END)
        
        automata = self.simulator.automata
        info = f"Estados: {', '.join(automata.states)}\n"
        info += f"Alfabeto: {', '.join(automata.alphabet)}\n"
        info += f"Estado inicial: {automata.initial_state}\n"
        info += f"Estados finales: {', '.join(automata.final_states)}\n\n"
        info += "Transiciones:\n"
        
        for state, trans in automata.transitions.items():
            for symbol, dests in trans.items():
                info += f"{state} --{symbol}--> {', '.join(dests)}\n"
                
        self.info_text.insert(tk.END, info)
        self.info_text['state'] = tk.DISABLED
        
    def draw_automata(self):
        if self.simulator.automata:
            self.automata_graph.draw_automata(
                states=self.simulator.automata.states,
                transitions=self.simulator.automata.transitions,
                initial_state=self.simulator.automata.initial_state,
                final_states=self.simulator.automata.final_states
            )
                
    def start_simulation(self):
        input_str = self.input_entry.get()
        if not input_str:
            messagebox.showerror("Error", "Ingrese una cadena para simular")
            return
            
        self.simulator.reset_simulation()
        self.simulator.simulate_string(input_str)
        self.display_simulation()
        
    def step_simulation(self):
        input_str = self.input_entry.get()
        if not input_str:
            messagebox.showerror("Error", "Ingrese una cadena para simular")
            return
            
        if len(self.simulator.simulation_history) >= len(input_str):
            messagebox.showinfo("Fin", "Simulación completada")
            return
            
        symbol = input_str[len(self.simulator.simulation_history)]
        self.simulator.step_simulation(symbol)
        self.display_simulation()
        
    def reset_simulation(self):
        self.simulator.reset_simulation()
        self.sim_text['state'] = tk.NORMAL
        self.sim_text.delete(1.0, tk.END)
        self.sim_text['state'] = tk.DISABLED
        if hasattr(self.simulator, 'automata') and self.simulator.automata:
            initial_state = self.simulator.automata.initial_state
            self.automata_graph.highlight_states({initial_state})
        
    def display_simulation(self):
        self.sim_text['state'] = tk.NORMAL
        self.sim_text.delete(1.0, tk.END)
        
        for i, step in enumerate(self.simulator.simulation_history, 1):
            self.sim_text.insert(tk.END, f"Paso {i}: Símbolo '{step['symbol']}'\n")
            self.sim_text.insert(tk.END, f"  Desde estados: {', '.join(step['from_states'])}\n")
            
            if step['transitions']:
                trans_text = []
                for trans in step['transitions']:
                    trans_text.append(f"{trans[0]} --{trans[1]}--> {trans[2]}")
                self.sim_text.insert(tk.END, f"  Transiciones: {'; '.join(trans_text)}\n")
            else:
                self.sim_text.insert(tk.END, "  No hay transiciones posibles\n")
                
            self.sim_text.insert(tk.END, f"  A estados: {', '.join(step['to_states']) if step['to_states'] else 'Ninguno'}\n")
            self.sim_text.insert(tk.END, f"  Aceptación: {'Sí' if step['is_accepted'] else 'No'}\n\n")
            
        self.sim_text['state'] = tk.DISABLED
        self.sim_text.see(tk.END)
        
        # Resaltar estado actual en el dibujo
        self.highlight_current_states()
        
    def highlight_current_states(self):
        if not self.simulator.simulation_history:
            return
        
        current_states = self.simulator.simulation_history[-1]['to_states']
        self.automata_graph.highlight_states(set(current_states))
        
    def setup_event_bindings(self):
        self.visual_frame.bind("<Configure>", self.on_canvas_resize)
    
    def on_canvas_resize(self, event):
        """Redibuja el autómata cuando cambia el tamaño del canvas"""
        if hasattr(self, 'automata_graph') and self.simulator.automata:
            self.automata_graph.update_canvas_size(event.width, event.height)
            self.draw_automata()
            if self.simulator.simulation_history:
                self.highlight_current_states()

    def load_automata_from_file(self):
        """Abre diálogo para cargar autómata desde archivo"""
        file_path = filedialog.askopenfilename(
            title="Cargar autómata",
            initialdir=os.path.join(os.path.dirname(__file__), "..", "examples"),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                automata = FileHandler.load_automata(file_path)
                self.simulator.load_automata(automata)
                self.update_automata_info()
                self.draw_automata()
                initial_state = automata.initial_state
                self.automata_graph.highlight_states({initial_state})
                self.step_btn['state'] = tk.NORMAL
                self.reset_btn['state'] = tk.NORMAL
                self.title(f"Simulador de Autómatas - {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el autómata:\n{str(e)}")

    def save_automata_to_file(self):
        """Abre diálogo para guardar autómata en archivo"""
        if not self.simulator.automata:
            messagebox.showerror("Error", "No hay autómata cargado para guardar")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Guardar autómata",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                name = os.path.splitext(os.path.basename(file_path))[0]
                FileHandler.save_automata(self.simulator.automata, file_path, name)
                messagebox.showinfo("Éxito", "Autómata guardado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el autómata:\n{str(e)}")