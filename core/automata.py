class Automata:
    def __init__(self, states, alphabet, transitions, initial_state, final_states):
        """
        Inicializa el autómata finito.
        
        :param states: Conjunto de estados (list)
        :param alphabet: Alfabeto de símbolos (list)
        :param transitions: Diccionario de transiciones 
            formato: {estado_actual: {símbolo: [estados_destino]}}
        :param initial_state: Estado inicial (str)
        :param final_states: Estados finales (list)
        """
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
        self.current_states = {initial_state}
        self.history = []
        
    def reset(self):
        """Reinicia el autómata al estado inicial"""
        self.current_states = {self.initial_state}
        self.history = []
        
    def step(self, symbol):
        """
        Realiza un paso de simulación con el símbolo dado.
        
        :param symbol: Símbolo de entrada
        :return: Tupla (estados_actuales, transiciones_usadas)
        """
        if symbol not in self.alphabet:
            raise ValueError(f"Símbolo '{symbol}' no está en el alfabeto")
            
        new_states = set()
        used_transitions = []
        
        for state in self.current_states:
            if state in self.transitions and symbol in self.transitions[state]:
                for dest_state in self.transitions[state][symbol]:
                    new_states.add(dest_state)
                    used_transitions.append((state, symbol, dest_state))
        
        self.history.append({
            'input': symbol,
            'from_states': self.current_states.copy(),
            'to_states': new_states.copy(),
            'transitions': used_transitions.copy()
        })
        
        self.current_states = new_states
        return new_states, used_transitions
        
    def is_accepted(self):
        """Verifica si el estado actual es de aceptación"""
        return any(state in self.final_states for state in self.current_states)
        
    def simulate(self, input_string):
        """Simula una cadena completa de entrada"""
        self.reset()
        for symbol in input_string:
            self.step(symbol)
        return self.is_accepted()