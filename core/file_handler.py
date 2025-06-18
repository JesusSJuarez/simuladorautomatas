import json
from pathlib import Path
from core.automata import Automata

class FileHandler:
    @staticmethod
    def load_automata(file_path: str) -> Automata:
        """Carga un autómata desde un archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            required_fields = ['states', 'alphabet', 'transitions', 'initial_state', 'final_states']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Falta campo requerido: {field}")
            
            return Automata(
                states=data['states'],
                alphabet=data['alphabet'],
                transitions=data['transitions'],
                initial_state=data['initial_state'],
                final_states=data['final_states']
            )
            
        except json.JSONDecodeError:
            raise ValueError("Archivo JSON inválido")
        except Exception as e:
            raise ValueError(f"Error al cargar autómata: {str(e)}")
    
    @staticmethod
    def save_automata(automata: Automata, file_path: str, name: str = ""):
        """Guarda un autómata en un archivo JSON"""
        data = {
            "name": name,
            "type": "FA",
            "states": automata.states,
            "alphabet": automata.alphabet,
            "transitions": automata.transitions,
            "initial_state": automata.initial_state,
            "final_states": automata.final_states
        }
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    
    @staticmethod
    def load_grammar(file_path: str) -> dict:
        """Carga una gramática desde un archivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                
            required_fields = ['variables', 'terminals', 'productions', 'start']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Falta campo requerido: {field}")
            
            return data
            
        except json.JSONDecodeError:
            raise ValueError("Archivo JSON inválido")
        except Exception as e:
            raise ValueError(f"Error al cargar gramática: {str(e)}")
    
    @staticmethod
    def save_grammar(grammar: dict, file_path: str, name: str = ""):
        """Guarda una gramática en un archivo JSON"""
        data = {
            "name": name,
            "type": "CFG",
            "variables": grammar['variables'],
            "terminals": grammar['terminals'],
            "productions": grammar['productions'],
            "start": grammar['start']
        }
        
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)