import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from core.turing_machine import TuringMachine
from core.file_handler_tm import TuringMachineFileHandler
from gui.turing_machine_gui.tape_display import TapeDisplay

class TuringMachineWindow(tk.Toplevel):
    """
    Ventana para la simulación paso a paso de una Máquina de Turing.
    Permite cargar, simular y visualizar el estado de la MT y la cinta.
    """
    def __init__(self, master):
        super().__init__(master)
        self.title("Simulador de Máquina de Turing")
        self.geometry("1200x800")
        self.turing_machine = None
        self.current_step_index = 0

        self.create_widgets()
        self.setup_layout()
        self.reset_ui() # Asegura que los botones estén deshabilitados al inicio

    def create_widgets(self):
        """Crea todos los widgets de la interfaz de usuario."""
        # --- Control Frame ---
        self.control_frame = ttk.LabelFrame(self, text="Control", padding=10)

        self.load_btn = ttk.Button(self.control_frame, text="Cargar MT", command=self.load_turing_machine_from_file)
        self.save_btn = ttk.Button(self.control_frame, text="Guardar MT", command=self.save_turing_machine_to_file)

        self.input_label = ttk.Label(self.control_frame, text="Cadena de entrada:")
        self.input_entry = ttk.Entry(self.control_frame, width=40)

        self.start_sim_btn = ttk.Button(self.control_frame, text="Iniciar Simulación", command=self.start_simulation)
        self.step_btn = ttk.Button(self.control_frame, text="Paso Siguiente", command=self.step_simulation, state=tk.DISABLED)
        self.prev_step_btn = ttk.Button(self.control_frame, text="Paso Anterior", command=self.prev_simulation_step, state=tk.DISABLED)
        self.reset_btn = ttk.Button(self.control_frame, text="Reiniciar", command=self.reset_simulation, state=tk.DISABLED)

        # --- Info Frame ---
        self.info_frame = ttk.LabelFrame(self, text="Información de la Máquina de Turing", padding=10)
        self.info_text = tk.Text(self.info_frame, height=15, state=tk.DISABLED, wrap=tk.WORD)

        # --- Simulation Log Frame ---
        self.log_frame = ttk.LabelFrame(self, text="Registro de Simulación", padding=10)
        self.log_text = tk.Text(self.log_frame, height=10, state=tk.DISABLED, wrap=tk.WORD)
        self.log_scrollbar = ttk.Scrollbar(self.log_frame, command=self.log_text.yview)
        self.log_text.config(yscrollcommand=self.log_scrollbar.set)

        # --- Tape Display Frame (contenedor para múltiples cintas) ---
        self.tape_display_container = ttk.LabelFrame(self, text="Cintas y Cabezas", padding=10)
        
        # Frame para contener el Canvas y el Scrollbar para las cintas
        self.tape_scrollable_frame = ttk.Frame(self.tape_display_container)
        self.tape_canvas = tk.Canvas(self.tape_scrollable_frame, bg='white', highlightbackground="gray", highlightthickness=1)
        self.tape_scrollbar_y = ttk.Scrollbar(self.tape_scrollable_frame, orient="vertical", command=self.tape_canvas.yview)
        
        self.tape_canvas.configure(yscrollcommand=self.tape_scrollbar_y.set)
        self.tape_canvas.bind('<Configure>', lambda e: self.tape_canvas.configure(scrollregion = self.tape_canvas.bbox("all")))
        
        # Frame interno que contendrá las cintas reales, dentro del canvas
        self.tape_inner_frame = ttk.Frame(self.tape_canvas)
        self.tape_canvas.create_window((0, 0), window=self.tape_inner_frame, anchor="nw")

        # Configurar el scrolling del ratón sobre el canvas
        self.tape_canvas.bind("<Enter>", self._bound_to_mousewheel)
        self.tape_canvas.bind("<Leave>", self._unbound_from_mousewheel)

        # Lista para mantener referencias a los widgets de cinta dinámicamente creados
        self.tape_widgets = [] 

    def setup_layout(self):
        """Organiza los widgets en la ventana."""
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(2, weight=1) # Log frame

        # Control Frame layout
        self.control_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.load_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.save_btn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.input_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.input_entry.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.start_sim_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        self.step_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.prev_step_btn.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        self.reset_btn.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        # Info Frame layout
        self.info_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.info_text.pack(expand=True, fill=tk.BOTH)

        # Tape Display Container layout - MODIFIED TO SPAN 2 ROWS
        self.tape_display_container.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=5, pady=5)
        self.tape_display_container.rowconfigure(0, weight=1)
        self.tape_display_container.columnconfigure(0, weight=1)
        
        # Colocar el frame scrollable dentro del contenedor principal de cintas
        self.tape_scrollable_frame.pack(fill=tk.BOTH, expand=True)
        self.tape_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tape_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Configurar el frame interno para que se expanda horizontalmente con el canvas
        self.tape_inner_frame.bind("<Configure>", lambda e: self.tape_canvas.configure(scrollregion = self.tape_canvas.bbox("all")))
        self.tape_inner_frame.bind("<Configure>", lambda e: self.tape_canvas.itemconfig(self.tape_canvas.winfo_children()[0], width=self.tape_canvas.winfo_width()))


        # Simulation Log Frame layout
        self.log_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.log_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_mousewheel(self, event):
        """Handles the mouse wheel event for the tape canvas scroll."""
        # Determine scroll direction based on OS
        if event.num == 5 or event.delta == -120:  # Scroll down
            self.tape_canvas.yview_scroll(1, "unit")
        elif event.num == 4 or event.delta == 120: # Scroll up
            self.tape_canvas.yview_scroll(-1, "unit")

    def _bound_to_mousewheel(self, event):
        """Binds the mouse wheel to the tape canvas when the pointer enters."""
        self.tape_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.tape_canvas.bind_all("<Button-5>", self._on_mousewheel)
        self.tape_canvas.bind_all("<MouseWheel>", self._on_mousewheel) # For Windows and Mac

    def _unbound_from_mousewheel(self, event):
        """Unbinds the mouse wheel from the tape canvas when the pointer leaves."""
        self.tape_canvas.unbind_all("<Button-4>")
        self.tape_canvas.unbind_all("<Button-5>")
        self.tape_canvas.unbind_all("<MouseWheel>")

    def reset_ui(self):
        """Resets the user interface to its initial state."""
        self.current_step_index = 0
        self.step_btn['state'] = tk.DISABLED
        self.prev_step_btn['state'] = tk.DISABLED
        self.reset_btn['state'] = tk.DISABLED
        self.input_entry.delete(0, tk.END)
        # Clear all existing tape widgets
        for widget in self.tape_widgets:
            widget.destroy()
        self.tape_widgets = []
        # Ensure the inner frame is also cleared and scroll is reset
        self.tape_canvas.delete("all")
        self.tape_inner_frame = ttk.Frame(self.tape_canvas)
        self.tape_canvas.create_window((0, 0), window=self.tape_inner_frame, anchor="nw")
        self.tape_inner_frame.bind("<Configure>", lambda e: self.tape_canvas.configure(scrollregion = self.tape_canvas.bbox("all")))
        self.tape_inner_frame.bind("<Configure>", lambda e: self.tape_canvas.itemconfig(self.tape_canvas.winfo_children()[0], width=self.tape_canvas.winfo_width()))
        
        self.update_info_text("")
        self.update_log_text("")

    def update_info_text(self, text):
        """Updates the TM information text box."""
        self.info_text['state'] = tk.NORMAL
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, text)
        self.info_text['state'] = tk.DISABLED

    def update_log_text(self, text):
        """Updates the simulation log text box."""
        self.log_text['state'] = tk.NORMAL
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, text)
        self.log_text['state'] = tk.DISABLED
        self.log_text.see(tk.END) # Auto-scroll

    def load_turing_machine_from_file(self):
        """Loads a Turing Machine from a JSON file."""
        file_path = filedialog.askopenfilename(
            title="Cargar Máquina de Turing",
            initialdir=os.path.join(os.path.dirname(__file__), "..", "..", "examples", "turing_machines"),
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                self.turing_machine = TuringMachineFileHandler.load_turing_machine_from_file(file_path)
                self.display_turing_machine_info()
                messagebox.showinfo("Éxito", "Máquina de Turing cargada correctamente.")
                self.reset_simulation() # Reset simulation when loading new TM
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la Máquina de Turing:\n{str(e)}")
                self.turing_machine = None
                self.reset_ui()

    def save_turing_machine_to_file(self):
        """Saves the current Turing Machine to a JSON file."""
        if not self.turing_machine:
            messagebox.showerror("Error", "No hay Máquina de Turing cargada para guardar.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Guardar Máquina de Turing",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                TuringMachineFileHandler.save_turing_machine_to_file(self.turing_machine, file_path)
                messagebox.showinfo("Éxito", "Máquina de Turing guardada correctamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la Máquina de Turing:\n{str(e)}")

    def display_turing_machine_info(self):
        """Displays the loaded Turing Machine information."""
        if not self.turing_machine:
            self.update_info_text("No hay Máquina de Turing cargada.")
            return

        info = f"Estados: {', '.join(sorted(list(self.turing_machine.states)))}\n"
        info += f"Alfabeto de entrada: {', '.join(sorted(list(self.turing_machine.alphabet)))}\n"
        info += f"Alfabeto de la cinta: {', '.join(sorted(list(self.turing_machine.tape_alphabet)))}\n"
        info += f"Estado inicial: {self.turing_machine.initial_state}\n"
        info += f"Símbolo de espacio en blanco: '{self.turing_machine.blank_symbol}'\n"
        info += f"Estados finales: {', '.join(sorted(list(self.turing_machine.final_states)))}\n"
        info += f"Tipo: {'Determinista' if self.turing_machine.is_deterministic else 'No Determinista'}\n\n"
        info += "Transiciones:\n"
        sorted_transitions_keys = sorted(self.turing_machine.transitions.keys(), key=lambda x: (x[0], x[1]))
        for (state, symbol) in sorted_transitions_keys:
            transitions_for_key = self.turing_machine.transitions[(state, symbol)]
            for next_state, write_symbol, move_direction in transitions_for_key:
                info += f"  ({state}, '{symbol}') -> ({next_state}, '{write_symbol}', {move_direction})\n"
        self.update_info_text(info)

    def start_simulation(self):
        """Starts the Turing Machine simulation with the input string."""
        if not self.turing_machine:
            messagebox.showerror("Error", "Primero debe cargar una Máquina de Turing.")
            return

        input_string = self.input_entry.get()
        if not input_string:
            messagebox.showerror("Error", "Ingrese una cadena de entrada para simular.")
            return

        # Validate that input symbols are in the input alphabet
        for char in input_string:
            if char not in self.turing_machine.alphabet:
                messagebox.showerror("Error de entrada",
                                     f"El símbolo '{char}' no está en el alfabeto de entrada de la MT.")
                return

        self.turing_machine.reset(input_string)
        self.current_step_index = 0
        self.update_simulation_display()
        self.step_btn['state'] = tk.NORMAL
        self.reset_btn['state'] = tk.NORMAL
        self.prev_step_btn['state'] = tk.DISABLED # Cannot go back at the beginning

    def step_simulation(self):
        """Advances one step in the Turing Machine simulation."""
        if not self.turing_machine:
            return

        # If we are at the end of the history, try to take a new step
        if self.current_step_index == len(self.turing_machine.history) - 1:
            if self.turing_machine.is_halted():
                messagebox.showinfo("Simulación Completada", "La Máquina de Turing se ha detenido en todos los caminos.")
                self.step_btn['state'] = tk.DISABLED
                return
            else:
                self.turing_machine.step() # Performs a new step, which adds new configurations to the history
        
        # Advance in the history index if possible
        if self.current_step_index < len(self.turing_machine.history) - 1:
            self.current_step_index += 1
            
        self.update_simulation_display()

        # Check if the simulation has finished after this step.
        current_configs_for_display = self.turing_machine.history[self.current_step_index]
        if not current_configs_for_display: # If there are no more active configurations
            messagebox.showinfo("Simulación Completada", "La Máquina de Turing se ha detenido en todos los caminos.")
            self.step_btn['state'] = tk.DISABLED
        elif self.turing_machine.is_accepted():
            messagebox.showinfo("Simulación Completada", "La Máquina de Turing ha ACEPTADO la cadena en al menos un camino.")
            self.step_btn['state'] = tk.DISABLED # Halts once a path accepts
        
    def prev_simulation_step(self):
        """Goes back one step in the Turing Machine simulation."""
        if not self.turing_machine:
            return

        if self.current_step_index > 0:
            self.current_step_index -= 1
        
        self.update_simulation_display()

    def reset_simulation(self):
        """Resets the Turing Machine simulation to the initial state."""
        if not self.turing_machine:
            return
        
        input_string = self.input_entry.get()
        if input_string: # Only if an input string is loaded
            self.turing_machine.reset(input_string)
            self.current_step_index = 0
            self.update_simulation_display()
            self.step_btn['state'] = tk.NORMAL
            self.prev_step_btn['state'] = tk.DISABLED
        else:
            self.reset_ui() # Clear everything if no input
            self.turing_machine = None # If reset without loaded TM
            self.display_turing_machine_info() # Update info text

    def update_simulation_display(self):
        """Updates the tape display, state, and simulation log."""
        if not self.turing_machine or not self.turing_machine.history:
            # Clear all existing tape widgets
            for widget_frame in self.tape_widgets:
                widget_frame.destroy()
            self.tape_widgets = []
            # Reset the inner frame and its window in the canvas
            self.tape_canvas.delete("all")
            self.tape_inner_frame = ttk.Frame(self.tape_canvas)
            self.tape_canvas.create_window((0, 0), window=self.tape_inner_frame, anchor="nw")
            self.tape_inner_frame.bind("<Configure>", lambda e: self.tape_canvas.configure(scrollregion = self.tape_canvas.bbox("all")))
            self.tape_inner_frame.bind("<Configure>", lambda e: self.tape_canvas.itemconfig(self.tape_canvas.winfo_children()[0], width=self.tape_canvas.winfo_width()))

            self.update_log_text("Inicie una simulación.")
            self.step_btn['state'] = tk.DISABLED
            self.prev_step_btn['state'] = tk.DISABLED
            return

        # Get configurations for the current step from history
        current_configs_for_display = self.turing_machine.history[self.current_step_index]

        # Clear all existing tape widgets before redrawing
        for widget_frame in self.tape_widgets:
            widget_frame.destroy()
        self.tape_widgets = []

        log_content = f"--- Paso {self.current_step_index} ---\n"

        if not current_configs_for_display:
            log_content += "No hay configuraciones activas en este paso (máquina detenida).\n"
            self.update_log_text(log_content)
        else:
            for i, (state, tape_tuple, head_pos) in enumerate(current_configs_for_display):
                # Convert tape tuple to list for visualization if TapeDisplay expects it
                tape_list = list(tape_tuple)

                # Create a LabelFrame for each tape, showing the state
                # Frames are now packed into tape_inner_frame
                path_frame = ttk.LabelFrame(self.tape_inner_frame, text=f"Camino {i+1} (Estado: {state})", padding=5)
                path_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
                self.tape_widgets.append(path_frame) # Save reference for future destruction

                # Create TapeDisplay inside this LabelFrame
                tape_display = TapeDisplay(path_frame, height=100)
                tape_display.pack(fill=tk.BOTH, expand=True)
                tape_display.set_tape(tape_list, head_pos)

                log_content += f"Camino {i+1}:\n"
                log_content += f"  Estado: '{state}'\n"
                log_content += f"  Cinta: '{''.join(tape_list)}'\n"
                log_content += f"  Cabeza en: {head_pos}\n"
                log_content += f"  Aceptado: {'Sí' if state in self.turing_machine.final_states else 'No'}\n\n"
            
            self.update_log_text(log_content)
            # Ensure the scrollregion is updated after adding widgets
            self.tape_canvas.update_idletasks() # Ensure widgets have size
            self.tape_canvas.config(scrollregion=self.tape_canvas.bbox("all"))


        # Enable/disable navigation buttons
        self.prev_step_btn['state'] = tk.NORMAL if self.current_step_index > 0 else tk.DISABLED
        
        # The next step button should be active if we haven't reached the end of the history
        # Or if we have reached the end of the history but the machine can still make more steps
        can_step_forward = False
        if self.current_step_index < len(self.turing_machine.history) - 1:
            can_step_forward = True # There are future steps in the history
        elif current_configs_for_display and not self.turing_machine.is_halted():
             can_step_forward = True # There may still be movements, even if history doesn't have more entries yet.
            
        self.step_btn['state'] = tk.NORMAL if can_step_forward else tk.DISABLED

        # Completion messages
        if self.turing_machine.is_halted() and not current_configs_for_display:
            # If there are no more active configurations and cannot advance.
            # Halt messages will be handled in step_simulation.
            pass
        elif self.turing_machine.is_accepted():
            # If at least one path accepts, the main simulation stops.
            # Acceptance messages will be handled in step_simulation.
            pass