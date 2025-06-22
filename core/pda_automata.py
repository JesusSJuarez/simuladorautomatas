import collections

class PushdownAutomata:
    """
    Inicializa un Autómata de Pila (AP).

    :param states: Conjunto de estados (lista de str)
    :param input_alphabet: Símbolos del alfabeto de entrada (lista de str)
    :param stack_alphabet: Símbolos del alfabeto de la pila (lista de str)
    :param transitions: Diccionario de transiciones en el formato:
        {
            (estado_actual, simbolo_entrada, simbolo_cima_pila): [
                (siguiente_estado, (simbolo_a_empujar1, simbolo_a_empujar2, ...))
            ]
        }
        - simbolo_entrada puede ser '' (transición epsilon en la entrada).
        - simbolo_cima_pila puede ser '' (transición epsilon en el desapilado de la pila).
        - simbolos_a_empujar puede ser ('') (transición epsilon en el apilado, lo que significa no empujar nada).
        - Para desapilar un símbolo y no empujar nada, usa ('',) para simbolos_a_empujar.
    :param initial_state: Estado inicial (str)
    :param initial_stack_symbol: Símbolo inicial en la pila (str)
    :param final_states: Estados finales (lista de str)
    """
    def __init__(self, states, input_alphabet, stack_alphabet, transitions,
                 initial_state, initial_stack_symbol, final_states):
        self.states = set(states)
        self.input_alphabet = set(input_alphabet)
        self.stack_alphabet = set(stack_alphabet)
        self.transitions = self._normalize_transitions(transitions)
        self.initial_state = initial_state
        self.initial_stack_symbol = initial_stack_symbol
        self.final_states = set(final_states)

        # Validar condiciones iniciales
        if self.initial_state not in self.states:
            raise ValueError(f"El estado inicial '{initial_state}' no está en los estados.")
        if self.initial_stack_symbol != '' and self.initial_stack_symbol not in self.stack_alphabet:
            raise ValueError(f"El símbolo inicial de la pila '{initial_stack_symbol}' no está en el alfabeto de la pila.")
        if not all(s in self.states for s in self.final_states):
            raise ValueError("Algunos estados finales no están en el conjunto de estados.")

        # La configuración inicial de la pila debe ser una tupla para consistencia.
        self.current_configurations = [(self.initial_state, (self.initial_stack_symbol,))]
        self.history = []

    def _normalize_transitions(self, transitions_raw):
        """
        Normaliza el diccionario de transiciones en bruto a un formato más utilizable,
        manejando los símbolos epsilon para la entrada y la pila.
        """
        normalized = collections.defaultdict(list)
        for (q, a, s_top), targets in transitions_raw.items():
            # Validar símbolos de transición
            if a != '' and a not in self.input_alphabet:
                raise ValueError(f"El símbolo de entrada '{a}' en la transición no está en el alfabeto de entrada.")
            if s_top != '' and s_top not in self.stack_alphabet:
                raise ValueError(f"El símbolo de la cima de la pila '{s_top}' en la transición no está en el alfabeto de la pila.")

            for next_q, push_symbols_raw in targets:
                if next_q not in self.states:
                    raise ValueError(f"El siguiente estado '{next_q}' en la transición no está en los estados.")
                
                # Convertir un solo string de símbolos a empujar a una tupla si es necesario
                # y asegurar que 'ε' se convierta a ''
                processed_push_symbols = []
                for s in push_symbols_raw:
                    if s == 'ε':
                        processed_push_symbols.append('')
                    else:
                        processed_push_symbols.append(s)
                push_symbols = tuple(processed_push_symbols)
                
                for s_push in push_symbols:
                    # Asegurarse de que el símbolo 'ε' se trata como cadena vacía para la lógica interna
                    if s_push != '' and s_push not in self.stack_alphabet:
                        raise ValueError(f"El símbolo a empujar '{s_push}' en la transición no está en el alfabeto de la pila.")

                normalized[(q, a, s_top)].append((next_q, push_symbols))
        return normalized

    def reset(self):
        """Reinicia el AP a su estado inicial y configuración de pila."""
        # Asegurar que la pila se inicialice como una tupla
        self.current_configurations = [(self.initial_state, (self.initial_stack_symbol,))]
        self.history = []

    def step(self, input_symbol):
        """
        Realiza un paso de simulación con el símbolo dado.
        
        :param input_symbol: El símbolo de entrada para este paso.
        :return: Tupla (nuevas_configuraciones, transiciones_usadas)
        """
        if input_symbol != '' and input_symbol not in self.input_alphabet:
            raise ValueError(f"El símbolo '{input_symbol}' no está en el alfabeto de entrada.")

        # Guardar una referencia a las configuraciones actuales para el historial
        # Asegurarse de que se guardan como [estado, lista_pila] para consistencia con el formato de historial
        current_configurations_before_step = [
            [state, list(stack_tuple)] for state, stack_tuple in self.current_configurations
        ]
        
        new_configurations = set() # Este set almacenará (estado, tupla_pila)
        used_transitions = []

        # Iterar sobre las configuraciones actuales (que son (estado, tupla_pila))
        for current_state, current_stack_tuple in self.current_configurations:
            # Obtener la cima de la pila (desde la tupla)
            stack_top = current_stack_tuple[-1] if current_stack_tuple else '' # '' si la pila está vacía

            # Intentar transiciones con el símbolo de entrada real y la cima de la pila
            potential_transitions = self.transitions.get((current_state, input_symbol, stack_top), [])
            
            # También considerar transiciones epsilon de entrada con la cima de la pila real
            potential_transitions.extend(self.transitions.get((current_state, '', stack_top), []))

            # También considerar transiciones de entrada reales con desapilado epsilon
            # Convertir tupla a lista para simular pop/push
            if current_stack_tuple: # Solo si la pila no está vacía
                potential_transitions.extend(self.transitions.get((current_state, input_symbol, ''), []))

            # Y epsilon de entrada y desapilado epsilon
            if current_stack_tuple: # Solo si la pila no está vacía
                potential_transitions.extend(self.transitions.get((current_state, '', ''), []))
            
            # Eliminar duplicados para múltiples rutas a la misma configuración
            unique_potential_transitions = []
            seen_configs = set()
            for next_q, push_symbols in potential_transitions:
                # Calcular cómo se vería la pila *sin* realizar aún el desapilado/apilado
                temp_stack = list(current_stack_tuple) # Convertir la tupla de pila a lista para manipulación temporal
                # Simular desapilado para la cima de pila no vacía (si la regla lo requiere)
                if stack_top != '' and temp_stack:
                    temp_stack.pop()
                # Simular desapilado para la cima de pila epsilon (si la regla lo requiere y la pila no está vacía)
                elif stack_top == '' and temp_stack:
                    pass # Mantener la pila como está por ahora, el desapilado real se maneja más tarde si es necesario

                # Simular apilado
                temp_stack.extend([s for s in push_symbols if s != ''])
                
                # Usar una tupla de (estado, tupla(pila)) para la verificación de unicidad
                config_tuple = (next_q, tuple(temp_stack)) 
                if config_tuple not in seen_configs:
                    unique_potential_transitions.append(((current_state, input_symbol, stack_top), (next_q, push_symbols)))
                    seen_configs.add(config_tuple)

            if not unique_potential_transitions:
                continue

            for (from_q, trans_input_sym, trans_stack_pop_sym), (next_q, push_symbols) in unique_potential_transitions:
                new_stack = list(current_stack_tuple) # Iniciar con la tupla original convertida a lista
                
                # Realizar desapilado basado en la regla de transición
                if trans_stack_pop_sym != '':
                    if not new_stack or new_stack[-1] != trans_stack_pop_sym:
                        continue
                    new_stack.pop()
                elif trans_stack_pop_sym == '' and not new_stack:
                    pass
                elif trans_stack_pop_sym == '' and new_stack:
                    pass
                
                # Realizar apilado basado en la regla de transición
                for s in reversed(push_symbols):
                    if s != '':
                        new_stack.append(s)
                
                # Convertir new_stack a una tupla antes de añadir a new_configurations
                new_config = (next_q, tuple(new_stack)) 
                new_configurations.add(new_config)
                used_transitions.append({
                    'from_state': from_q,
                    'input_symbol': trans_input_sym,
                    'stack_pop_symbol': trans_stack_pop_sym,
                    'to_state': next_q,
                    'stack_push_symbols': push_symbols,
                    'from_stack': list(current_stack_tuple), # Registrar la pila original como lista para el historial
                    'to_stack': list(new_stack) # Registrar la pila resultante como lista para el historial
                })
        
        # Solo registrar el historial si es un paso con un símbolo de entrada real.
        if input_symbol != '':
            self.history.append({
                'input_symbol': input_symbol,
                'from_configurations': current_configurations_before_step,
                'to_configurations': [list(c) for c in new_configurations], # Convertir set de tuplas a lista de listas
                'transitions_used': used_transitions.copy(),
                'is_accepted': self.is_accepted()
            })
        
        # Actualizar el estado interno del AP con la nueva lista de configuraciones (tuplas)
        self.current_configurations = list(new_configurations) 
        return new_configurations, used_transitions

    def is_accepted(self):
        """
        Verifica si alguna configuración actual es una configuración de aceptación.
        La aceptación puede ser alcanzando un estado final o teniendo una pila vacía
        en un estado final, dependiendo de la definición del AP. Para este simulador,
        aceptaremos por estado final O pila vacía.
        """
        for state, stack_tuple in self.current_configurations:
            if state in self.final_states:
                return True
            # Opcional: Agregar aceptación por pila vacía si se desea, p. ej., y not stack_tuple:
            # if state in self.final_states and not stack_tuple: # Si la pila es una tupla vacía
            #     return True
        return False

    def simulate(self, input_string):
        """Simula una cadena de entrada completa."""
        self.reset()
        for symbol in input_string:
            # Nota: Este método ya no maneja directamente el cierre epsilon,
            # ya que eso lo gestiona PDASimulator para el paso a paso.
            # Para una simulación completa, la lógica de PDASimulator.simulate_full_string es la correcta.
            self.step(symbol)
            # Aplicar cierre epsilon después de cada paso de entrada
            changed_epsilon = True
            while changed_epsilon:
                old_configs_len = len(self.current_configurations)
                epsilon_new_configs, _ = self.perform_epsilon_moves()
                self.current_configurations.extend(list(epsilon_new_configs.difference(self.current_configurations)))
                self.current_configurations = list(set(self.current_configurations)) # Eliminar duplicados
                if len(self.current_configurations) == old_configs_len:
                    changed_epsilon = False

            if not self.current_configurations:
                break
        
        # Aplicar cierre epsilon final
        changed_epsilon = True
        while changed_epsilon:
            old_configs_len = len(self.current_configurations)
            epsilon_new_configs, _ = self.perform_epsilon_moves()
            self.current_configurations.extend(list(epsilon_new_configs.difference(self.current_configurations)))
            self.current_configurations = list(set(self.current_configurations))
            if len(self.current_configurations) == old_configs_len:
                changed_epsilon = False

        return self.is_accepted()

    def get_current_states(self):
        """Devuelve el conjunto de estados actuales."""
        return {q for q, _ in self.current_configurations}

    def get_current_stack(self):
        """Devuelve la(s) pila(s) de las configuraciones actuales.
           Nota: Con AP no deterministas, puede haber múltiples pilas.
           Para simplicidad, devolveremos la primera pila si existen varias.
        """
        if self.current_configurations:
            # Devolver la pila como una lista, para que sea mutable si es necesario para el consumo externo
            return list(self.current_configurations[0][1]) 
        return []

    def perform_epsilon_moves(self):
        """
        Realiza una ronda de movimientos épsilon desde las configuraciones actuales.
        Devuelve (nuevas_configuraciones_generadas_en_la_ronda, lista_de_transiciones_usadas_en_la_ronda).
        NO actualiza self.current_configurations ni el historial.
        """
        new_configs_in_round = set()
        transitions_in_round = []

        for config_tuple in self.current_configurations:
            path_new_configs, path_transitions = self._process_single_config_for_transition(config_tuple, '') # Buscar input epsilon
            new_configs_in_round.update(path_new_configs)
            transitions_in_round.extend(path_transitions)
        
        return new_configs_in_round, transitions_in_round

    def is_accepted_on_configs(self, configs_to_check):
        """Verifica si alguna configuración en el conjunto dado es de aceptación."""
        for state, stack_tuple in configs_to_check:
            if state in self.final_states:
                return True
        return False
