import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from core.grammar import ContextFreeGrammar
from core.file_handler import FileHandler
from .derivation_tree import DerivationTree
import os

class GrammarWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Simulador de Gramática Libre de Contexto")
        self.geometry("800x600")
        self.parent = parent
        
        self.grammar = None
        self.grammar_engine = None
        self.current_step = 0
        
        self.create_widgets()
        self.setup_layout()
        
    def create_widgets(self):
        # Panel de control
        self.control_frame = ttk.LabelFrame(self, text="Control", padding=10)
        
        self.load_btn = ttk.Button(
            self.control_frame, 
            text="Cargar Gramática", 
            command=self.load_grammar
        )
        
        self.input_label = ttk.Label(self.control_frame, text="Cadena a derivar:")
        self.input_entry = ttk.Entry(self.control_frame, width=30)
        
        self.step_btn = ttk.Button(
            self.control_frame, 
            text="Paso a Paso", 
            command=self.step_derivation,
            state=tk.DISABLED
        )
        
        self.reset_btn = ttk.Button(
            self.control_frame, 
            text="Reiniciar", 
            command=self.reset_derivation,
            state=tk.DISABLED
        )
        
        # Panel de información
        self.info_frame = ttk.LabelFrame(self, text="Gramática", padding=10)
        self.info_text = tk.Text(self.info_frame, height=10, state=tk.DISABLED)
        
        # Panel de derivación
        self.deriv_frame = ttk.LabelFrame(self, text="Derivación", padding=10)
        self.deriv_text = tk.Text(self.deriv_frame, height=15, state=tk.DISABLED)
        
        # Panel de árbol
        self.tree_frame = ttk.LabelFrame(self, text="Árbol de Derivación", padding=10)
        self.tree_canvas = DerivationTree(self.tree_frame)
        
    def setup_layout(self):
        # Configuración de grid
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)
        
        # Control frame
        self.control_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.input_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.input_entry.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.step_btn.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.reset_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        
        # Info frame
        self.info_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.info_text.pack(expand=True, fill=tk.BOTH)
        
        # Deriv frame
        self.deriv_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.deriv_text.pack(expand=True, fill=tk.BOTH)
        
        # Tree frame
        self.tree_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.tree_canvas.pack(expand=True, fill=tk.BOTH)
        
    def load_grammar(self):
        file_path = filedialog.askopenfilename(
            title="Cargar gramática",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                grammar_data = FileHandler.load_grammar(file_path)
                self.grammar = grammar_data
                self.grammar_engine = ContextFreeGrammar(
                    variables=grammar_data['variables'],
                    terminals=grammar_data['terminals'],
                    productions=grammar_data['productions'],
                    start_symbol=grammar_data['start']
                )
                self.update_grammar_info()
                self.step_btn['state'] = tk.NORMAL
                self.reset_btn['state'] = tk.NORMAL
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la gramática:\n{str(e)}")
    
    def update_grammar_info(self):
        self.info_text['state'] = tk.NORMAL
        self.info_text.delete(1.0, tk.END)
        
        info = f"Variables: {', '.join(self.grammar['variables'])}\n"
        info += f"Terminales: {', '.join(self.grammar['terminals'])}\n"
        info += f"Símbolo inicial: {self.grammar['start']}\n\n"
        info += "Producciones:\n"
        
        for var, prods in self.grammar['productions'].items():
            info += f"{var} → {' | '.join(prods)}\n"
                
        self.info_text.insert(tk.END, info)
        self.info_text['state'] = tk.DISABLED
    
    def step_derivation(self):
        if not self.grammar_engine:
            messagebox.showerror("Error", "No hay gramática cargada")
            return
            
        step = self.grammar_engine.step_derivation()
        if step is None:
            messagebox.showinfo("Fin", "No hay más variables para expandir")
            return
            
        self.display_derivation_step(step)
        self.tree_canvas.draw_step(step, self.grammar_engine.derivation_history)
    
    def display_derivation_step(self, step):
        self.deriv_text['state'] = tk.NORMAL
        self.deriv_text.insert(tk.END, f"Paso {len(self.grammar_engine.derivation_history)}:\n")
        self.deriv_text.insert(tk.END, f"  {step['from']}\n")
        self.deriv_text.insert(tk.END, f"  Aplicando {step['variable']} → {step['production']}\n")
        self.deriv_text.insert(tk.END, f"  Obtenemos: {step['to']}\n\n")
        self.deriv_text['state'] = tk.DISABLED
        self.deriv_text.see(tk.END)
    
    def reset_derivation(self):
        if self.grammar_engine:
            self.grammar_engine.reset_derivation()
        self.deriv_text['state'] = tk.NORMAL
        self.deriv_text.delete(1.0, tk.END)
        self.deriv_text['state'] = tk.DISABLED
        self.tree_canvas.clear()

    def step_derivation(self):
        if not self.grammar_engine:
            messagebox.showerror("Error", "No hay gramática cargada")
            return

        # Mostrar diálogo para seleccionar producción si hay múltiples opciones
        possible_steps = self.grammar_engine.get_possible_steps()
        if len(possible_steps) > 1:
            step = self._ask_production_choice(possible_steps)
            if step is None:  # Usuario canceló
                return
        else:
            step = None  # Usará la única disponible

        step_info = self.grammar_engine.step_derivation(
            variable=step['variable'] if step else None,
            production=step['production'] if step else None
        )

        if step_info is None:
            messagebox.showinfo("Fin", "No hay más variables para expandir")
            return

        self.display_derivation_step(step_info)
        self.tree_canvas.draw_step(step_info, self.grammar_engine.derivation_history)

    def _ask_production_choice(self, possible_steps):
        """Muestra diálogo para seleccionar producción"""
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar producción")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Seleccione la producción a aplicar:").pack(pady=10)
        
        listbox = tk.Listbox(dialog)
        for i, step in enumerate(possible_steps):
            listbox.insert(i, f"{step['variable']} → {step['production']}")
        listbox.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        selected_step = None
        
        def on_select():
            nonlocal selected_step
            selection = listbox.curselection()
            if selection:
                selected_step = possible_steps[selection[0]]
                dialog.destroy()
        
        ttk.Button(dialog, text="Aplicar", command=on_select).pack(pady=10)
        
        dialog.wait_window()
        return selected_step

    def derive_string(self):
        """Deriva automáticamente la cadena objetivo"""
        input_str = self.input_entry.get()
        if not input_str:
            messagebox.showerror("Error", "Ingrese una cadena para derivar")
            return
            
        success, history = self.grammar_engine.derive_string(input_str)
        
        if success:
            self.deriv_text['state'] = tk.NORMAL
            self.deriv_text.delete(1.0, tk.END)
            for step in history:
                self.display_derivation_step(step)
            messagebox.showinfo("Éxito", "Cadena derivada exitosamente")
        else:
            messagebox.showerror("Error", "No se pudo derivar la cadena")