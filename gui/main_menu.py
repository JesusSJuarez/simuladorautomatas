import tkinter as tk
from tkinter import ttk
from gui.automata_gui.window import AutomataWindow

class MainMenu(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Simulador de Autómatas - Menú Principal")
        self.geometry("400x300")
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Seleccione qué desea simular",
            font=("Arial", 14)
        )
        title_label.pack(pady=10)
        
        # Botones de opciones
        automata_btn = ttk.Button(
            main_frame,
            text="Simular Autómata",
            command=self.open_automata_simulator,
            width=20
        )
        automata_btn.pack(pady=10)
        
        # Espacio para futuros botones
        # future_btn = ttk.Button(...)
        # future_btn.pack(pady=10)
        
        # Botón de salida
        exit_btn = ttk.Button(
            main_frame,
            text="Salir",
            command=self.destroy,
            width=20
        )
        exit_btn.pack(pady=20)
        
    def open_automata_simulator(self):
        """Abre la ventana de simulación de autómatas"""
        self.withdraw()  # Oculta el menú principal
        automata_window = AutomataWindow(self)
        automata_window.protocol("WM_DELETE_WINDOW", lambda: self.on_automata_close(automata_window))
        
    def on_automata_close(self, window):
        """Maneja el cierre de la ventana de autómatas"""
        window.destroy()
        self.deiconify()  # Muestra nuevamente el menú principal