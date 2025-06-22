import json
from core.turing_machine import TuringMachine

class TuringMachineFileHandler:
    """
    Maneja la carga y guardado de Máquinas de Turing desde/hacia archivos JSON.
    """
    @staticmethod
    def load_turing_machine_from_file(file_path):
        """
        Carga una Máquina de Turing desde un archivo JSON.

        Args:
            file_path (str): Ruta al archivo JSON.

        Returns:
            TuringMachine: Una instancia de TuringMachine.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        states = set(data['states'])
        alphabet = set(data['alphabet'])
        tape_alphabet = set(data['tape_alphabet'])
        initial_state = data['initial_state']
        blank_symbol = data['blank_symbol']
        final_states = set(data['final_states'])

        transitions = {}
        for (state_symbol_key, next_steps) in data['transitions'].items():
            state, symbol = eval(state_symbol_key) # Evalúa la tupla como cadena
            transitions[(state, symbol)] = [tuple(step) for step in next_steps]

        return TuringMachine(states, alphabet, tape_alphabet, transitions, initial_state, blank_symbol, final_states)

    @staticmethod
    def save_turing_machine_to_file(turing_machine, file_path):
        """
        Guarda una Máquina de Turing en un archivo JSON.

        Args:
            turing_machine (TuringMachine): La instancia de TuringMachine a guardar.
            file_path (str): Ruta al archivo JSON.
        """
        data = {
            'states': list(turing_machine.states),
            'alphabet': list(turing_machine.alphabet),
            'tape_alphabet': list(turing_machine.tape_alphabet),
            'transitions': { str(k): v for k, v in turing_machine.transitions.items() }, # Convertir tuplas de clave a string
            'initial_state': turing_machine.initial_state,
            'blank_symbol': turing_machine.blank_symbol,
            'final_states': list(turing_machine.final_states)
        }
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
