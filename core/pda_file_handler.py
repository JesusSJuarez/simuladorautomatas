import json
from pathlib import Path
from core.pda_automata import PushdownAutomata

class PDAFileHandler:
    """
    Gestiona la carga y guardado de Autómatas de Pila a/desde archivos JSON.
    """
    @staticmethod
    def load_pda_from_file(file_path: str) -> PushdownAutomata:
        """
        Carga un Autómata de Pila desde un archivo JSON.

        :param file_path: Ruta al archivo JSON.
        :return: Una instancia de PushdownAutomata.
        :raises ValueError: Si el archivo es inválido o faltan campos requeridos.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # Validar estructura básica para AP
            required_fields = [
                'states', 'input_alphabet', 'stack_alphabet', 'transitions',
                'initial_state', 'initial_stack_symbol', 'final_states'
            ]
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"El archivo JSON no contiene el campo requerido: '{field}'")
            
            # Normalizar transiciones de claves JSON (que deben ser strings) de vuelta a tuplas
            # Las claves JSON solo pueden ser strings, así que esperamos el formato "estado,entrada,cima_pila"
            normalized_transitions = {}
            for key_str, targets in data['transitions'].items():
                parts = key_str.split(',')
                if len(parts) != 3:
                    raise ValueError(f"Formato de clave de transición inválido: '{key_str}'. Se esperaba 'estado,simbolo_entrada,simbolo_cima_pila'.")
                
                # Manejar string vacío para epsilon en claves JSON
                state = parts[0]
                input_sym = parts[1] if parts[1] != 'ε' else '' # 'ε' para epsilon en JSON
                stack_top = parts[2] if parts[2] != 'ε' else '' # 'ε' para epsilon en JSON

                parsed_targets = []
                for next_state, push_list_raw in targets:
                    # Convertir la lista de símbolos a empujar (lista de strings) a tupla de strings, manejar epsilon
                    parsed_push_list = tuple([s if s != 'ε' else '' for s in push_list_raw])
                    parsed_targets.append((next_state, parsed_push_list))
                
                normalized_transitions[(state, input_sym, stack_top)] = parsed_targets

            return PushdownAutomata(
                states=data['states'],
                input_alphabet=data['input_alphabet'],
                stack_alphabet=data['stack_alphabet'],
                transitions=normalized_transitions,
                initial_state=data['initial_state'],
                initial_stack_symbol=data['initial_stack_symbol'],
                final_states=data['final_states']
            )

        except json.JSONDecodeError:
            raise ValueError("El archivo no es un JSON válido.")
        except Exception as e:
            raise ValueError(f"Error al cargar el AP: {str(e)}")

    @staticmethod
    def save_pda_to_file(pda: PushdownAutomata, file_path: str, name: str = ""):
        """
        Guarda un Autómata de Pila en un archivo JSON.

        :param pda: La instancia de PushdownAutomata a guardar.
        :param file_path: Ruta al archivo JSON.
        :param name: Nombre opcional para el autómata.
        """
        # Convertir transiciones (cuyas claves son tuplas) a un formato serializable en JSON (cuyas claves son strings)
        serializable_transitions = {}
        for (q, a, s_top), targets in pda.transitions.items():
            # Usar 'ε' para epsilon para una mejor legibilidad en JSON
            input_sym_str = a if a != '' else 'ε'
            stack_top_str = s_top if s_top != '' else 'ε'
            key_str = f"{q},{input_sym_str},{stack_top_str}"
            
            serializable_targets = []
            for next_q, push_symbols in targets:
                # Convertir la tupla de símbolos a empujar a una lista de strings, usar 'ε' para epsilon
                serializable_push_symbols = [s if s != '' else 'ε' for s in push_symbols]
                serializable_targets.append([next_q, serializable_push_symbols])
            
            serializable_transitions[key_str] = serializable_targets

        data = {
            "name": name,
            "type": "PDA",
            "states": sorted(list(pda.states)),
            "input_alphabet": sorted(list(pda.input_alphabet)),
            "stack_alphabet": sorted(list(pda.stack_alphabet)),
            "transitions": serializable_transitions,
            "initial_state": pda.initial_state,
            "initial_stack_symbol": pda.initial_stack_symbol,
            "final_states": sorted(list(pda.final_states))
        }

        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
