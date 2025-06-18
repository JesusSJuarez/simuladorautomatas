from collections import deque
from collections import deque

class ContextFreeGrammar:
    def __init__(self, variables, terminals, productions, start_symbol):
        self.variables = variables
        self.terminals = terminals
        self.productions = productions
        self.start_symbol = start_symbol
        self.reset_derivation()

    def reset_derivation(self):
        self.current_derivation = self.start_symbol
        self.derivation_history = []
        self.possible_steps = []
        self._update_possible_steps()

    def _update_possible_steps(self):
        """Actualiza las posibles producciones aplicables"""
        self.possible_steps = []
        for i, char in enumerate(self.current_derivation):
            if char in self.variables:
                for prod in self.productions[char]:
                    self.possible_steps.append({
                        'position': i,
                        'variable': char,
                        'production': prod
                    })

    def get_possible_steps(self):
        """Devuelve las posibles producciones aplicables"""
        return self.possible_steps

    def step_derivation(self, variable=None, production=None):
        """
        Realiza un paso de derivación.
        Si no se especifica variable y producción, usa la primera posible.
        """
        if not self.possible_steps:
            return None

        if variable and production:
            # Buscar el paso específico
            step = next((s for s in self.possible_steps 
                        if s['variable'] == variable and s['production'] == production), None)
            if not step:
                raise ValueError("Producción no válida para la variable especificada")
        else:
            # Usar el primer paso disponible (comportamiento por defecto)
            step = self.possible_steps[0]

        # Aplicar la producción
        new_derivation = (self.current_derivation[:step['position']] + 
                         step['production'] + 
                         self.current_derivation[step['position']+1:])

        step_info = {
            'from': self.current_derivation,
            'variable': step['variable'],
            'production': step['production'],
            'to': new_derivation,
            'position': step['position']
        }

        self.current_derivation = new_derivation
        self.derivation_history.append(step_info)
        self._update_possible_steps()

        return step_info

    def derive_string(self, input_string):
        """
        Intenta derivar la cadena de entrada usando backtracking
        Devuelve (success, history)
        """
        self.reset_derivation()
        return self._derive_recursive(input_string, [])

    def _derive_recursive(self, target, history):
        if self.current_derivation == target:
            return True, history.copy()

        if not self.possible_steps:
            return False, None

        # Ordenar producciones para probar primero las más prometedoras
        sorted_steps = sorted(self.possible_steps, 
                            key=lambda x: self._production_heuristic(x, target))

        for step in sorted_steps:
            # Aplicar el paso
            current_state = self.current_derivation
            self.current_derivation = (current_state[:step['position']] + 
                                     step['production'] + 
                                     current_state[step['position']+1:])
            history.append({
                'from': current_state,
                'variable': step['variable'],
                'production': step['production'],
                'to': self.current_derivation,
                'position': step['position']
            })
            self._update_possible_steps()

            # Llamada recursiva
            success, result = self._derive_recursive(target, history)
            if success:
                return True, result

            # Backtrack
            self.current_derivation = current_state
            history.pop()
            self._update_possible_steps()

        return False, None

    def _production_heuristic(self, step, target):
        """
        Heurística para seleccionar la mejor producción:
        1. Prefiere producciones que acerquen la longitud al objetivo
        2. Prefiere producciones que empiecen con el mismo símbolo que el objetivo
        """
        # Calcular la nueva derivación si aplicamos este paso
        new_deriv = (self.current_derivation[:step['position']] + 
                    step['production'] + 
                    self.current_derivation[step['position']+1:])
        
        # Puntuación basada en longitud
        length_score = abs(len(new_deriv) - len(target))
        
        # Puntuación basada en prefijos coincidentes
        prefix_score = 0
        min_len = min(len(new_deriv), len(target))
        for i in range(min_len):
            if new_deriv[i] == target[i]:
                prefix_score += 1
            else:
                break
                
        return length_score * 0.6 + (min_len - prefix_score) * 0.4