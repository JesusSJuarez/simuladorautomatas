import json
from pathlib import Path
from automata import Automata

class AutomataFileHandler:
    @staticmethod
    def load_automata_from_file(file_path: str) -> Automata:
        """Carga un autómata desde un archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            # Validar estructura básica
            required_fields = ['states', 'alphabet', 'transitions', 'initial_state', 'final_states']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"El archivo JSON no contiene el campo requerido: {field}")
            
            return Automata(
                states=data['states'],
                alphabet=data['alphabet'],
                transitions=data['transitions'],
                initial_state=data['initial_state'],
                final_states=data['final_states']
            )
            
        except json.JSONDecodeError:
            raise ValueError("El archivo no es un JSON válido")
        except Exception as e:
            raise ValueError(f"Error al cargar el autómata: {str(e)}")
    
    @staticmethod
    def save_automata_to_file(automata: Automata, file_path: str, name: str = ""):
        """Guarda un autómata en un archivo JSON"""
        data = {
            "name": name,
            "type": "DFA",
            "states": automata.states,
            "alphabet": automata.alphabet,
            "transitions": automata.transitions,
            "initial_state": automata.initial_state,
            "final_states": automata.final_states
        }
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)