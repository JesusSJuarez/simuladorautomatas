import tkinter as tk
from tkinter import ttk
from gui.automata_gui.window import AutomataWindow
from gui.regex_gui.app_gui import RegexSimulatorApp
from gui.automatas_pila.pda_window import PDAWindow # Importar la nueva ventana del simulador de AP

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador - Menú Principal")
        self.geometry("400x350")
        self._setup_ui()

    def _setup_ui(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(main_frame, text="Seleccione una opción:", font=('Arial', 14)).pack(pady=10)
        
        options = [
            ("Autómatas Finitos", self._open_automata),
            ("Autómatas de Pila", self._open_pda), # Añadir esta nueva opción
            ("Expresiones Regulares", self._open_regex),
            ("Salir", self.destroy)
        ]
        
        for text, cmd in options:
            btn = ttk.Button(main_frame, text=text, command=cmd, width=20)
            btn.pack(pady=5)

    def _open_automata(self):
        self.withdraw()
        window = AutomataWindow(self)
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))

    def _open_pda(self): # Nuevo método para abrir la ventana de AP
        self.withdraw()
        window = PDAWindow(self)
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))

    def _open_regex(self):
        self.withdraw()
        window = tk.Toplevel(self)
        RegexSimulatorApp(window)
        window.protocol("WM_DELETE_WINDOW", lambda: self._on_child_close(window))


    def _on_child_close(self, window):
        window.destroy()
        self.deiconify()
