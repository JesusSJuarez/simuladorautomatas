class TuringMachine:
    """
    Representa una Máquina de Turing de una sola cinta.
    Soporta máquinas deterministas y no deterministas.
    """
    def __init__(self, states, alphabet, tape_alphabet, transitions, initial_state, blank_symbol, final_states):
        """
        Inicializa la Máquina de Turing.

        Args:
            states (set): Conjunto de estados de la MT.
            alphabet (set): Alfabeto de entrada.
            tape_alphabet (set): Alfabeto de la cinta (incluye el símbolo de espacio en blanco).
            transitions (dict): Diccionario de transiciones.
                                Formato: { (estado_actual, simbolo_leido): [(nuevo_estado, simbolo_escrito, movimiento), ...] }
                                Movimiento: 'L' (izquierda), 'R' (derecha), 'S' (estacionario).
            initial_state (str): Estado inicial.
            blank_symbol (str): Símbolo de espacio en blanco en la cinta.
            final_states (set): Conjunto de estados finales (aceptación).
        """
        self.states = states
        self.alphabet = alphabet
        self.tape_alphabet = tape_alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.blank_symbol = blank_symbol
        self.final_states = final_states
        # current_configurations ahora es una lista de (estado, tupla_cinta, cabeza_pos)
        self.current_configurations = []
        # history ahora almacena una lista de listas de configuraciones para cada paso
        self.history = []
        self.is_deterministic = self._check_determinism()

        # Validaciones básicas
        if initial_state not in states:
            raise ValueError("El estado inicial no está en el conjunto de estados.")
        if not all(s in states for s in final_states):
            raise ValueError("Algún estado final no está en el conjunto de estados.")
        if blank_symbol not in tape_alphabet:
            raise ValueError("El símbolo de espacio en blanco no está en el alfabeto de la cinta.")
        if not alphabet.issubset(tape_alphabet):
            raise ValueError("El alfabeto de entrada debe ser un subconjunto del alfabeto de la cinta.")

    def _check_determinism(self):
        """
        Verifica si la Máquina de Turing es determinista.
        Una MT es determinista si para cada (estado, símbolo_leído), hay a lo sumo una transición.
        """
        for (state, symbol) in self.transitions:
            if len(self.transitions[(state, symbol)]) > 1:
                return False
        return True

    def reset(self, input_string):
        """
        Reinicia la máquina de Turing con una nueva cadena de entrada.

        Args:
            input_string (str): La cadena de entrada para la simulación.
        """
        tape = list(input_string)
        # Asegurarse de que la cinta tenga al menos un símbolo en blanco a cada lado
        # Añadimos 10 blancos a cada lado.
        tape = [self.blank_symbol] * 10 + tape + [self.blank_symbol] * 10
        # Corregir la posición inicial de la cabeza para que esté sobre un símbolo en blanco
        # antes del inicio de la cadena de entrada.
        head_pos = 9 # Posición inicial de la cabeza (un símbolo antes del inicio de la cadena de entrada)
        
        # current_configurations ahora es una lista con la configuración inicial
        initial_config = (self.initial_state, tuple(tape), head_pos)
        self.current_configurations = [initial_config]
        
        self.history = []
        # El historial del paso 0 es la configuración inicial
        self.history.append([initial_config]) 

    def step(self):
        """
        Realiza un paso de simulación de la Máquina de Turing.
        Actualiza las configuraciones actuales según las transiciones.

        Returns:
            bool: True si se realizó al menos un paso válido, False si no hay más transiciones posibles.
        """
        if not self.current_configurations:
            # Si no hay configuraciones activas, la máquina ya ha parado en todos los caminos.
            return False 

        next_configurations = set()
        moved = False # Flag para saber si al menos una configuración pudo avanzar

        # Iterar sobre una copia de las configuraciones actuales para evitar problemas al modificarlas
        configurations_to_process = list(self.current_configurations)
        
        for current_state, tape_tuple, current_head_pos in configurations_to_process:
            current_tape_list = list(tape_tuple) # Convertir tupla de la cinta a lista para operaciones mutables

            # Expandir la cinta si la cabeza está en los bordes
            while current_head_pos < 0:
                current_tape_list.insert(0, self.blank_symbol)
                current_head_pos += 1
            while current_head_pos >= len(current_tape_list):
                current_tape_list.append(self.blank_symbol)

            current_symbol = current_tape_list[current_head_pos]

            # Buscar transiciones
            if (current_state, current_symbol) in self.transitions:
                possible_transitions = self.transitions[(current_state, current_symbol)]
                moved_this_config = False # Flag para saber si esta configuración particular se movió

                for next_state, write_symbol, move_direction in possible_transitions:
                    new_tape_list = list(current_tape_list) # Copia de la cinta (potencialmente expandida)
                    new_tape_list[current_head_pos] = write_symbol
                    new_head_pos = current_head_pos

                    if move_direction == 'L':
                        new_head_pos -= 1
                    elif move_direction == 'R':
                        new_head_pos += 1
                    # 'S' significa estacionario, no hay cambio en new_head_pos

                    next_configurations.add((next_state, tuple(new_tape_list), new_head_pos))
                    moved = True # Al menos una configuración se ha movido
                    moved_this_config = True # Esta configuración se ha movido
                
                # Si esta configuración se movió, y es no determinista, se generaron nuevas configuraciones
                # que serán el siguiente paso. Si no se movió (no_determinista, pero solo un camino posible
                # que luego se bloquea), entonces no se añade nada para esta configuración.
                if not moved_this_config and not self.is_deterministic:
                     # Si no se encontró ninguna transición para esta configuración específica,
                     # se bloquea o termina en este camino.
                     pass # Ya no se añade a next_configurations
            else:
                # Si no se encuentra ninguna transición para esta configuración (estado, símbolo), se bloquea.
                pass # Esta configuración simplemente no se añade a next_configurations
                                     
        self.current_configurations = list(next_configurations) # Actualizar configuraciones activas
        
        # Añadir al historial las configuraciones resultantes de este paso.
        # Si next_configurations está vacía, indica que todos los caminos se han detenido.
        self.history.append(list(next_configurations))
        
        return moved # Retornar true si alguna configuración se movió exitosamente

    def is_accepted(self):
        """
        Verifica si alguna de las configuraciones actuales ha alcanzado un estado de aceptación.
        """
        for state, _, _ in self.current_configurations:
            if state in self.final_states:
                return True
        return False

    def is_halted(self):
        """
        Verifica si la máquina ha parado (no hay más transiciones posibles para ninguna configuración).
        """
        # La máquina ha parado si no hay configuraciones activas.
        return not self.current_configurations