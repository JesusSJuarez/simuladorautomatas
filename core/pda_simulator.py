from tkinter import messagebox # Se importa aquí para usar en los mensajes de error/información

from core.pda_automata import PushdownAutomata

class PDASimulator:
    """
    Gestiona la simulación de un Autómata de Pila.
    """
    def __init__(self):
        self.pda: PushdownAutomata = None
        self.input_string = ""
        self.current_step_index = 0
        self.simulation_history = []
        self.is_finished = False

    def load_pda(self, pda: PushdownAutomata):
        """Carga un AP en el simulador."""
        self.pda = pda
        self.reset_simulation()

    def set_input_string(self, input_str: str):
        """Establece la cadena de entrada para la simulación."""
        self.input_string = input_str
        self.reset_simulation()

    def reset_simulation(self):
        """Reinicia la simulación a su estado inicial y aplica el cierre epsilon inicial."""
        if self.pda:
            # Reinicia el PDA interno
            self.pda.reset()
            self.current_step_index = 0
            self.simulation_history = []
            self.is_finished = False
            # Aplica el cierre epsilon inicial y registra en el historial
            self._apply_epsilon_closure_and_record(initial_step=True) 
        else:
            self.current_step_index = 0
            self.simulation_history = []
            self.is_finished = False

    def _apply_epsilon_closure_and_record(self, initial_step=False):
        """
        Aplica transiciones epsilon desde el conjunto actual de configuraciones hasta que no
        se generen nuevas configuraciones. Registra cada ronda de cierre epsilon como un paso
        separado en el historial, si hay cambios.
        """
        original_configs_for_closure = set(tuple(c) for c in self.pda.current_configurations)
        current_closure_configs = original_configs_for_closure.copy()
        
        changed_in_closure = True
        all_epsilon_transitions_fired = []

        while changed_in_closure:
            changed_in_closure = False
            new_configs_in_round = set()
            transitions_in_round = []

            for state, stack_tuple in list(current_closure_configs): # Iterar sobre una copia para permitir modificaciones
                current_stack_list = list(stack_tuple)

                # Replicar la lógica de pda.step para transiciones epsilon desde esta configuración
                stack_top = current_stack_list[-1] if current_stack_list else ''
                
                potential_epsilon_transitions = self.pda.transitions.get((state, '', stack_top), [])
                potential_epsilon_transitions.extend(self.pda.transitions.get((state, '', ''), []))
                
                for next_q, push_symbols in potential_epsilon_transitions:
                    temp_stack = list(current_stack_list)
                    
                    # Determinar el símbolo de desapilado de la regla específica
                    rule_pop_symbol = ''
                    # Buscar la regla específica para determinar el símbolo de desapilado correcto
                    found_rule = False
                    if (state, '', stack_top) in self.pda.transitions:
                        for target_next_q, target_push_symbols in self.pda.transitions[(state, '', stack_top)]:
                            if target_next_q == next_q and target_push_symbols == push_symbols:
                                rule_pop_symbol = stack_top
                                found_rule = True
                                break
                    if not found_rule and (state, '', '') in self.pda.transitions:
                         for target_next_q, target_push_symbols in self.pda.transitions[(state, '', '')]:
                            if target_next_q == next_q and target_push_symbols == push_symbols:
                                rule_pop_symbol = '' # Pop epsilon
                                found_rule = True
                                break
                    if not found_rule:
                        continue # No debería ocurrir si las reglas están bien formadas

                    # Aplicar desapilado (si el símbolo de la regla no es epsilon y la pila coincide)
                    if rule_pop_symbol != '':
                        if not temp_stack or temp_stack[-1] != rule_pop_symbol:
                            continue
                        temp_stack.pop()
                    
                    # Aplicar apilado
                    for s_push in reversed(push_symbols):
                        if s_push != '':
                            temp_stack.append(s_push)
                    
                    new_config_tuple = (next_q, tuple(temp_stack))
                    if new_config_tuple not in current_closure_configs and new_config_tuple not in new_configs_in_round:
                        new_configs_in_round.add(new_config_tuple)
                        changed_in_closure = True
                        
                        # Registrar los detalles de esta transición epsilon específica
                        transitions_in_round.append({
                            'from_state': state,
                            'input_symbol': '', # Entrada epsilon
                            'stack_pop_symbol': rule_pop_symbol,
                            'to_state': next_q,
                            'stack_push_symbols': push_symbols,
                            'from_stack': list(stack_tuple), # Guardar como lista para el historial
                            'to_stack': list(temp_stack) # Guardar como lista para el historial
                        })
            
            current_closure_configs.update(new_configs_in_round)
            all_epsilon_transitions_fired.extend(transitions_in_round)

        # Actualizar las configuraciones actuales del PDA a la clausura final
        self.pda.current_configurations = list(current_closure_configs)

        # Registrar este cierre epsilon en el historial SOLO si se alcanzaron nuevas configuraciones
        # o si es el paso inicial (para mostrar la configuración inicial antes de cualquier entrada)
        if initial_step or current_closure_configs != original_configs_for_closure:
            self.simulation_history.append({
                'input_symbol': 'ε-cierre', # Marcador especial para el cierre epsilon
                'configurations_before': [list(c) for c in original_configs_for_closure], # Convertir a lista para historial
                'configurations_after': [list(c) for c in current_closure_configs], # Convertir a lista para historial
                'transitions_used': all_epsilon_transitions_fired,
                'is_accepted': self.pda.is_accepted_on_configs(current_closure_configs)
            })

    def step_simulation(self):
        """
        Realiza un paso lógico de la simulación: procesa un símbolo de entrada
        (o maneja los movimientos epsilon finales). Incluye el cierre epsilon
        antes y después de procesar el símbolo de entrada.
        Devuelve True si se realizó un paso (se avanzó), False en caso contrario
        (simulación terminada/atascada).
        """
        if not self.pda:
            messagebox.showerror("Error", "No hay AP cargado.")
            return False

        if self.is_finished:
            return False

        made_progress_in_this_step = False
        
        # Obtener el símbolo a procesar para este paso lógico
        symbol_to_process = None
        if self.current_step_index < len(self.input_string):
            symbol_to_process = self.input_string[self.current_step_index]
            self.current_step_index += 1
            
            # Almacenar configuraciones antes de procesar este símbolo de entrada
            configs_before_symbol_processing = [list(c) for c in self.pda.current_configurations]

            # Realizar el paso en el PDA
            new_configs_from_input, transitions_used_from_input = self.pda.step(symbol_to_process)
            
            if new_configs_from_input:
                self.pda.current_configurations = new_configs_from_input
                made_progress_in_this_step = True
            else: # El PDA se atascó en este símbolo de entrada
                self.is_finished = True
                self.pda.current_configurations = [] # Borrar configuraciones
                
                # Registrar este paso atascado
                self.simulation_history.append({
                    'input_symbol': symbol_to_process,
                    'configurations_before': configs_before_symbol_processing,
                    'configurations_after': [],
                    'transitions_used': transitions_used_from_input,
                    'is_accepted': False
                })
                return True # Indicar que intentamos procesar un símbolo y nos atascamos
            
            # Registrar el paso del símbolo de entrada real
            self.simulation_history.append({
                'input_symbol': symbol_to_process,
                'configurations_before': configs_before_symbol_processing,
                'configurations_after': [list(c) for c in new_configs_from_input], # Asegurar que es lista de listas
                'transitions_used': transitions_used_from_input,
                'is_accepted': self.pda.is_accepted() and self.current_step_index == len(self.input_string) # Check acceptance with full input consumption
            })
            
            # Ahora, aplicar el cierre epsilon después de procesar el símbolo de entrada
            self._apply_epsilon_closure_and_record()
            
            if not self.pda.current_configurations: # Si se atascó después del cierre epsilon
                self.is_finished = True
            elif self.pda.is_accepted() and self.current_step_index == len(self.input_string): # Final acceptance check
                self.is_finished = True # Aceptado después del símbolo final + cierre epsilon

            return made_progress_in_this_step

        else: # La cadena de entrada está agotada. Continuar solo con transiciones epsilon.
            
            # Intentar hacer más movimientos epsilon hasta que no se encuentren nuevas configuraciones
            num_history_before_epsilon_only = len(self.simulation_history)
            self._apply_epsilon_closure_and_record()
            
            if len(self.simulation_history) == num_history_before_epsilon_only:
                # No se agregó un nuevo paso de cierre epsilon, lo que significa que no se encontraron nuevas configuraciones.
                self.is_finished = True
                return False # No se puede avanzar más

            made_progress_in_this_step = True # Los pasos epsilon hicieron progreso

            if not self.pda.current_configurations: # Atascado
                self.is_finished = True
            elif self.pda.is_accepted() and self.current_step_index == len(self.input_string): # Final acceptance check
                self.is_finished = True # Aceptado por movimientos epsilon
            
            return made_progress_in_this_step


    def simulate_full_string(self):
        """Simula la cadena de entrada completa, incluyendo todos los cierres epsilon necesarios."""
        self.reset_simulation() # Esto ya aplica el cierre epsilon inicial
        if not self.pda:
            messagebox.showerror("Error", "No hay AP cargado.")
            return False

        # Continuar avanzando hasta que termine
        while not self.is_finished:
            if not self.step_simulation(): # step_simulation devuelve False si no hay más movimientos posibles
                break
        
        return self.is_simulation_accepted() # Use the refined acceptance check


    def get_current_states_for_display(self):
        """Devuelve los estados de las configuraciones actuales para resaltar."""
        if self.simulation_history:
            # Obtener estados de las 'configurations_after' del último paso
            last_step_configs = self.simulation_history[-1]['configurations_after']
            return {config[0] for config in last_step_configs}
        elif self.pda:
            # Si aún no hay historial, devolver el estado inicial
            return {self.pda.initial_state}
        return set()

    def get_current_stack_for_display(self):
        """
        Devuelve la(s) pila(s) de las configuraciones actuales para mostrar.
        Dado que un AP no determinista puede tener múltiples pilas, esto devuelve una lista de pilas.
        """
        if self.simulation_history:
            last_step_configs = self.simulation_history[-1]['configurations_after']
            return [config[1] for config in last_step_configs]
        elif self.pda:
            return [[self.pda.initial_stack_symbol]]
        return [[]] # Pila vacía por defecto si no hay AP o historial

    def get_last_step_details(self):
        """Devuelve los detalles del último paso de simulación realizado."""
        if self.simulation_history:
            return self.simulation_history[-1]
        return None

    def get_current_input_symbol(self):
        """Devuelve el símbolo de entrada que se está procesando en el paso actual."""
        # Si estamos al final de la cadena de entrada, el símbolo actual es 'ε' para los movimientos epsilon.
        if self.current_step_index > len(self.input_string) and self.is_finished:
             return 'FIN (ε)'
        elif self.current_step_index < len(self.input_string):
            return self.input_string[self.current_step_index - 1] # Símbolo *recién procesado*
        return 'N/A' # Si la simulación aún no ha comenzado o está en estado inicial

    def get_remaining_input(self):
        """Devuelve la porción de la cadena de entrada que aún no se ha procesado."""
        return self.input_string[self.current_step_index:]

    def is_simulation_accepted(self):
        """
        Verifica si la simulación actual es aceptada.
        Esto implica que el AP está en un estado final Y que toda la cadena de entrada ha sido consumida.
        """
        if not self.pda:
            return False

        # La simulación es aceptada si se alcanzó un estado final y se ha consumido toda la entrada.
        # En el caso de simulaciones paso a paso o completas, el `current_step_index`
        # debe ser igual a la longitud de la cadena de entrada.
        # Y debe haber al menos una configuración actual en un estado final.
        return self.current_step_index == len(self.input_string) and self.pda.is_accepted()
