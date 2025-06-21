from core.automata import Automata

class AutomataSimulator:
    def __init__(self, automata=None):
        self.automata = automata
        self.simulation_history = []
        
    def load_automata(self, automata):
        """Carga un autómata para simular"""
        self.automata = automata
        self.reset_simulation()
        
    def reset_simulation(self):
        """Reinicia la simulación"""
        if self.automata:
            self.automata.reset()
        self.simulation_history = []
        
    def step_simulation(self, symbol):
        """
        Realiza un paso de simulación y guarda el historial
        
        :return: Dict con información del paso
        """
        if not self.automata:
            raise ValueError("No hay autómata cargado")
            
        current_states, transitions = self.automata.step(symbol)
        
        step_info = {
            'symbol': symbol,
            'from_states': self.automata.history[-1]['from_states'],
            'to_states': current_states,
            'transitions': transitions,
            'is_accepted': self.automata.is_accepted()
        }
        
        self.simulation_history.append(step_info)
        return step_info
        
    def simulate_string(self, input_string):
        """Simula una cadena completa"""
        self.reset_simulation()
        results = []
        for symbol in input_string:
            results.append(self.step_simulation(symbol))
        return results