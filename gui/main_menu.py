import tkinter as tk
from tkinter import ttk
from gui.automata_gui.window import AutomataWindow
from gui.regex_gui.app_gui import RegexSimulatorApp
from gui.automatas_pila.pda_window import PDAWindow # Importar la ventana del simulador de AP
from gui.grammar_gui.gui_app import CFGSimulatorApp # Importar la nueva ventana del simulador de GLC
from gui.turing_machine_gui.app_gui import TuringMachineWindow # Importar la ventana del simulador de MT

class MainMenu(tk.Tk):
    """
    Clase principal para el menú de la aplicación de simuladores.
    Extiende tk.Tk para crear la ventana principal.
    """
    def __init__(self):
        super().__init__()
        self.title("Simulador - Menú Principal")
        self.geometry("400x350")
        self._setup_ui()

    def _setup_ui(self):
        """
        Configura la interfaz de usuario del menú principal.
        Crea botones para abrir diferentes simuladores.
        """
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="Seleccione una opción:", font=('Arial', 14)).pack(pady=10)
        
        options = [
            ("Autómatas Finitos", self._open_automata),
            ("Autómatas de Pila", self._open_pda),
            ("Gramáticas Libres de Contexto", self._open_cfg), # Añadir esta nueva opción para GLC
            ("Expresiones Regulares", self._open_regex),
            ("Máquina de Turing", self._open_turing_machine), # Nueva opción para Máquina de Turing
            ("Salir", self.destroy)
        ]
        
        for text, cmd in options:
            btn = ttk.Button(main_frame, text=text, command=cmd, width=20)
            btn.pack(pady=5)

    def _open_automata(self):
        self.withdraw()
        window = AutomataWindow(self)
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))

    def _open_pda(self):
        self.withdraw()
        window = PDAWindow(self)
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))

    def _open_cfg(self): # Nuevo método para abrir la ventana del simulador de GLC
        self.withdraw()
        window = tk.Toplevel(self) # Las aplicaciones Tkinter a menudo usan Toplevel para nuevas ventanas
        cfg_app = CFGSimulatorApp(window) # Instanciar la aplicación CFGSimulatorApp
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))

    def _open_regex(self):
        self.withdraw()
        window = tk.Toplevel(self)
        RegexSimulatorApp(window)
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))

    def _open_turing_machine(self): # Nuevo método para abrir la ventana del simulador de MT
        """
        Abre la ventana del simulador de Máquina de Turing.
        Oculta la ventana del menú principal mientras la ventana de la Máquina de Turing está abierta.
        """
        self.withdraw()  # Oculta la ventana principal
        window = TuringMachineWindow(self)
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))

    def _on_child_close(self, window):
        """
        Maneja el cierre de una ventana secundaria.
        Destruye la ventana secundaria y vuelve a mostrar la ventana del menú principal.
        """
        window.destroy()
        self.deiconify() # Vuelve a mostrar la ventana principal

if __name__ == "__main__":
    app = MainMenu()
    app.mainloop()