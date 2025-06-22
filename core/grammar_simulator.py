# grammar_simulator.py

class CFGSimulator:
    """
    Clase para simular derivaciones de Gramáticas Libres de Contexto (GLC) paso a paso.
    """
    def __init__(self, display_step_callback, ask_for_choice_callback, display_message_callback, clear_choices_callback):
        """
        Inicializa el simulador con callbacks para interactuar con la interfaz gráfica.

        Args:
            display_step_callback (function): Función para mostrar un paso de la derivación.
            ask_for_choice_callback (function): Función para solicitar una elección al usuario.
            display_message_callback (function): Función para mostrar mensajes de estado/error.
            clear_choices_callback (function): Función para limpiar las opciones de elección.
        """
        self.grammar = {}
        self.current_string = ''
        self.target_string = ''
        self.step_count = 0
        self.is_simulating = False
        self.current_leftmost_non_terminal_index = -1

        # Callbacks para la UI
        self.display_step_callback = display_step_callback
        self.ask_for_choice_callback = ask_for_choice_callback
        self.display_message_callback = display_message_callback
        self.clear_choices_callback = clear_choices_callback

    def parse_grammar(self, rules_text):
        """
        Parsea las reglas de producción del texto de entrada a un diccionario.
        Formato esperado: "NoTerminal->Produccion1 | Produccion2"

        Args:
            rules_text (str): El texto de entrada de las reglas.

        Returns:
            dict: Un diccionario donde las claves son no-terminales y los valores son listas de producciones.

        Raises:
            ValueError: Si el formato de alguna regla es inválido.
        """
        parsed_rules = {}
        lines = rules_text.split('\n')
        lines = [line.strip() for line in lines if line.strip()] # Limpiar líneas vacías

        if not lines:
            raise ValueError("No se han proporcionado reglas de producción.")

        for line in lines:
            parts = line.split('->')
            if len(parts) != 2:
                raise ValueError(f"Formato de regla inválido: \"{line}\". Use \"NoTerminal->Produccion\".")

            non_terminal = parts[0].strip()
            productions = parts[1].strip().split('|')
            productions = [p.strip() for p in productions] # Limpiar espacios en producciones

            if not self._is_non_terminal(non_terminal) or len(non_terminal) != 1:
                raise ValueError(f"Símbolo no-terminal inválido: \"{non_terminal}\" en \"{line}\". Debe ser una sola letra mayúscula.")

            if non_terminal in parsed_rules:
                parsed_rules[non_terminal].extend(productions)
            else:
                parsed_rules[non_terminal] = productions
        return parsed_rules

    def _is_non_terminal(self, char):
        """
        Verifica si un carácter es un no-terminal (letra mayúscula).

        Args:
            char (str): El carácter a verificar.

        Returns:
            bool: True si es un no-terminal, False en caso contrario.
        """
        return len(char) == 1 and 'A' <= char <= 'Z'

    def find_leftmost_non_terminal(self, string):
        """
        Encuentra el índice del no-terminal más a la izquierda en la cadena actual.

        Args:
            string (str): La cadena actual.

        Returns:
            int: El índice del no-terminal, o -1 si no se encuentra ninguno.
        """
        for i, char in enumerate(string):
            if self._is_non_terminal(char):
                return i
        return -1

    def get_possible_productions(self, non_terminal):
        """
        Obtiene las producciones posibles para un no-terminal dado.

        Args:
            non_terminal (str): El no-terminal.

        Returns:
            list: Una lista de producciones para el no-terminal.
        """
        return self.grammar.get(non_terminal, [])

    def apply_production(self, string, index, production):
        """
        Aplica una producción a la cadena actual en el índice del no-terminal.

        Args:
            string (str): La cadena original.
            index (int): El índice del no-terminal a reemplazar.
            production (str): La producción a sustituir.

        Returns:
            str: La nueva cadena después de la sustitución.
        """
        before = string[:index]
        after = string[index + 1:]
        # Si la producción es 'ε' (cadena vacía), se elimina el no-terminal.
        return before + ('' if production == 'ε' else production) + after

    def start_simulation(self, rules_text, start_symbol, target_string):
        """
        Inicia la simulación.
        Valida las entradas y prepara el estado inicial.

        Args:
            rules_text (str): Texto con las reglas de producción.
            start_symbol (str): Símbolo inicial de la gramática.
            target_string (str): Cadena objetivo a derivar.
        """
        if self.is_simulating:
            self.display_message_callback('Ya hay una simulación en curso. Reinicie para empezar una nueva.', 'info')
            return

        try:
            self.clear_choices_callback()
            self.display_message_callback('') # Limpiar mensaje anterior
            self.step_count = 0
            self.is_simulating = True

            # 1. Parsear reglas de gramática
            self.grammar = self.parse_grammar(rules_text)
            start_symbol = start_symbol.strip()
            self.target_string = target_string.strip()

            if not start_symbol:
                raise ValueError('Por favor, ingrese un símbolo inicial.')
            if not self._is_non_terminal(start_symbol) or len(start_symbol) != 1:
                raise ValueError('El símbolo inicial debe ser una sola letra mayúscula.')
            if not self.target_string:
                raise ValueError('Por favor, ingrese la cadena a simular.')
            if start_symbol not in self.grammar:
                raise ValueError(f"El símbolo inicial '{start_symbol}' no tiene reglas de producción definidas.")

            self.current_string = start_symbol
            self.display_step_callback(self.step_count, self.current_string)
            self.process_next_step()

        except ValueError as e:
            self.display_message_callback(f"Error al iniciar: {e}", 'error')
            self.is_simulating = False # Permitir reintento
        except Exception as e:
            self.display_message_callback(f"Un error inesperado ocurrió: {e}", 'error')
            self.is_simulating = False

    def process_next_step(self):
        """
        Procesa el siguiente paso de la derivación.
        Determina si se necesita una elección del usuario o si se puede proceder automáticamente.
        """
        self.current_leftmost_non_terminal_index = self.find_leftmost_non_terminal(self.current_string)

        # Si no hay más no-terminales
        if self.current_leftmost_non_terminal_index == -1:
            self._end_simulation()
            return

        non_terminal = self.current_string[self.current_leftmost_non_terminal_index]
        possible_productions = self.get_possible_productions(non_terminal)

        if not possible_productions:
            self.display_message_callback(f"Error: El no-terminal '{non_terminal}' no tiene producciones definidas. La simulación ha terminado.", 'error')
            self.is_simulating = False
            return

        if len(possible_productions) == 1:
            # Si solo hay una producción posible, aplícala automáticamente
            chosen_production = possible_productions[0]
            self.perform_step(chosen_production)
        else:
            # Si hay múltiples producciones, solicita la elección del usuario
            self.ask_for_choice_callback(non_terminal, possible_productions)

    def perform_step(self, chosen_production):
        """
        Realiza un paso de la simulación con la producción elegida.
        Este método es llamado por la UI después de que el usuario hace una elección.

        Args:
            chosen_production (str): La producción seleccionada por el usuario o automáticamente.
        """
        self.clear_choices_callback() # Oculta los botones de elección una vez que se ha hecho una.

        # Aplicar la producción
        old_string = self.current_string
        self.current_string = self.apply_production(self.current_string, self.current_leftmost_non_terminal_index, chosen_production)
        self.step_count += 1

        # Mostrar el paso en la UI
        self.display_step_callback(
            self.step_count,
            self.current_string,
            old_string,
            self.current_leftmost_non_terminal_index,
            chosen_production
        )

        # Continuar con el siguiente paso
        self.process_next_step()

    def _end_simulation(self):
        """
        Finaliza la simulación y valida si la cadena final coincide con la objetivo.
        """
        self.is_simulating = False
        if self.current_string == self.target_string:
            self.display_message_callback(f"¡Simulación completa! La cadena '{self.target_string}' fue derivada exitosamente.", 'success')
        else:
            self.display_message_callback(f"Simulación completa. La cadena final '{self.current_string}' no coincide con la cadena objetivo '{self.target_string}'.", 'error')

    def reset_simulation(self):
        """
        Reinicia el estado del simulador.
        """
        self.grammar = {}
        self.current_string = ''
        self.target_string = ''
        self.step_count = 0
        self.is_simulating = False
        self.current_leftmost_non_terminal_index = -1
        self.clear_choices_callback()
        self.display_message_callback('')

