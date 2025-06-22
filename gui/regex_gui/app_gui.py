import tkinter as tk
from tkinter import scrolledtext, messagebox
from core.regex_logic import RegexSimulator

class RegexSimulatorApp:
    def __init__(self, master: tk.Toplevel):
        self.master = master
        master.title("Simulador de Expresiones Regulares")
        master.geometry("800x500")
        master.resizable(True, True)

        # Configuración de estilo para consistencia con el menú principal
        master.option_add('*Font', 'Arial 10')
        master.option_add('*LabelFrame.Label.Font', 'Arial 12 bold')
        master.option_add('*Button.Font', 'Arial 10 bold')

        # --- Frames para organizar la interfaz ---
        # Frame de entrada: Contiene el patrón regex, el texto y el botón de simular.
        self.input_frame = tk.LabelFrame(master, text="Entrada", padx=15, pady=15, bd=2, relief="groove")
        self.input_frame.pack(padx=15, pady=10, fill="x", expand=False)

        # Frame de resultados: Muestra la coincidencia completa.
        self.output_frame = tk.LabelFrame(master, text="Resultados de la Simulación", padx=15, pady=15, bd=2, relief="groove")
        self.output_frame.pack(padx=15, pady=10, fill="x", expand=False)

        # La sección de "Traza de Validación Paso a Paso del Texto" ha sido eliminada de la GUI.

        # Frame de explicación: Muestra la explicación paso a paso del patrón regex.
        self.explanation_frame = tk.LabelFrame(master, text="Explicación Detallada del Patrón Regex", padx=15, pady=15, bd=2, relief="groove")
        self.explanation_frame.pack(padx=15, pady=10, fill="both", expand=True)


        # --- Widgets del Frame de Entrada ---
        tk.Label(self.input_frame, text="Patrón Regex:").pack(anchor="w", pady=(0, 2))
        self.regex_entry = tk.Entry(self.input_frame, width=80, bd=2, relief="solid")
        self.regex_entry.pack(fill="x", pady=5)
        # Ejemplo de patrón por defecto (número de teléfono)
        self.regex_entry.insert(0, r"(\d{3})-(\d{3}-\d{4})")

        tk.Label(self.input_frame, text="Cadena a Comprobar:").pack(anchor="w", pady=(5, 2))
        # Cambiado de ScrolledText a Entry para una sola línea
        self.text_input = tk.Entry(self.input_frame, width=80, bd=2, relief="solid")
        self.text_input.pack(fill="x", pady=5)
        # Ejemplo de texto por defecto (ahora una sola cadena)
        self.text_input.insert(0, "123-456-7890")

        self.simulate_button = tk.Button(self.input_frame, text="Simular Expresión Regular",
                                         command=self.run_simulation,
                                         bg="#4CAF50", fg="white", activebackground="#45a049",
                                         relief="raised", bd=3, padx=10, pady=5)
        self.simulate_button.pack(pady=10)

        # --- Widgets del Frame de Resultados ---
        tk.Label(self.output_frame, text="Coincidencia Completa Encontrada:").pack(anchor="w", pady=(0, 2))
        self.full_match_label = tk.Label(self.output_frame, text="Esperando simulación...",
                                         bg="#e0e0e0", fg="black", wraplength=700,
                                         justify="left", anchor="w", padx=5, pady=5, bd=1, relief="solid")
        self.full_match_label.pack(fill="x", pady=5)



        # --- Widgets del Frame de Explicación ---
        self.explanation_text = scrolledtext.ScrolledText(self.explanation_frame, width=80, height=12,
                                                          wrap=tk.WORD, bg="#e6f7ff", bd=1, relief="solid")
        self.explanation_text.pack(fill="both", expand=True, pady=5)
        self.explanation_text.config(state=tk.DISABLED) # Hacerlo de solo lectura

    def run_simulation(self):
        """
        Función que se ejecuta cuando se presiona el botón "Simular".
        Obtiene los valores de entrada, llama a la lógica del simulador
        y actualiza la interfaz con los resultados y explicaciones.
        """
        pattern = self.regex_entry.get()
        # Obtener el texto del widget Entry (ya no ScrolledText)
        text = self.text_input.get().strip()

        # Instanciar la lógica del simulador
        simulator = RegexSimulator(pattern, text)
        success = simulator.run_simulation()

        # Limpiar resultados anteriores en la GUI
        self.full_match_label.config(text="", bg="#e0e0e0")
        self.explanation_text.config(state=tk.NORMAL)
        self.explanation_text.delete("1.0", tk.END)
        self.explanation_text.config(state=tk.DISABLED)
        # Se elimina la limpieza de validation_trace_text


        if not success:
            # Si hubo un error en el patrón regex, mostrar el error en la explicación
            explanation = simulator.get_step_by_step_explanations()
            if explanation:
                self.explanation_text.config(state=tk.NORMAL)
                self.explanation_text.insert(tk.END, "\n".join(explanation))
                self.explanation_text.config(state=tk.DISABLED)
            # Se elimina la visualización del error en la traza de validación

            self.full_match_label.config(text="Error: Patrón de expresión regular inválido. Por favor, revise el patrón.", bg="#ffcccc")
            return

        # --- Mostrar información de la coincidencia completa ---
        full_match_info = simulator.get_full_match_info()
        if full_match_info["found"]:
            self.full_match_label.config(text=f"Coincidencia: '{full_match_info['match_string']}' "
                                             f"(Índice de inicio: {full_match_info['start_index']}, "
                                             f"Índice de fin: {full_match_info['end_index']})", bg="#d4edda") # Verde claro para éxito
        else:
            self.full_match_label.config(text="No se encontró ninguna coincidencia completa.", bg="#f8d7da") # Rojo claro para no encontrado

        # La sección de "Grupos Capturados" ha sido eliminada de la GUI
        # La sección de "Traza de Validación Paso a Paso del Texto" ha sido eliminada de la GUI.

        # --- Mostrar la explicación paso a paso del patrón regex ---
        explanations = simulator.get_step_by_step_explanations()
        self.explanation_text.config(state=tk.NORMAL) # Habilitar para escribir
        if explanations:
            for i, exp in enumerate(explanations):
                self.explanation_text.insert(tk.END, f"{i+1}. {exp}\n")
        else:
            self.explanation_text.insert(tk.END, "No hay explicación disponible para este patrón (quizás es demasiado simple o hubo un error al parsearlo).")
        self.explanation_text.config(state=tk.DISABLED) # Deshabilitar después de escribir

# Este bloque asegura que la aplicación se ejecute solo cuando el script es el principal
if __name__ == "__main__":
    root = tk.Tk()
    app = RegexSimulatorApp(root)
    root.mainloop()
