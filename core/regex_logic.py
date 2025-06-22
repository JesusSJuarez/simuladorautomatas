import re

class RegexSimulator:
    """
    Clase para simular y explicar patrones de expresiones regulares.
    Proporciona información sobre coincidencias completas, grupos capturados
    y una explicación componente a componente del patrón regex.
    """
    def __init__(self, pattern: str, text: str):
        """
        Inicializa el simulador con un patrón regex y un texto de entrada.

        Args:
            pattern (str): La expresión regular a simular.
            text (str): El texto en el que buscar coincidencias.
        """
        self.pattern = pattern
        self.text = text
        self.match = None
        self.explanations = [] # Almacena las explicaciones paso a paso del regex (del patrón)
        self.validation_trace = [] # Almacena la traza de validación (del texto)

    def run_simulation(self) -> bool:
        """
        Ejecuta la simulación de la expresión regular contra el texto.
        Genera las explicaciones del patrón regex independientemente del resultado de la coincidencia.
        Si se encuentra una coincidencia, también genera la traza de validación.

        Returns:
            bool: True si la expresión regular es válida y se pudo intentar la coincidencia,
                  False si hay un error en el patrón regex.
        """
        self.explanations = []
        self.validation_trace = []
        try:
            # Intentar encontrar la primera coincidencia del patrón en el texto
            self.match = re.search(self.pattern, self.text)
            # Generar explicaciones del patrón regex. Esto se hace incluso si no hay coincidencia.
            self._generate_regex_explanations()

            if self.match:
                # Si hay una coincidencia, generar la traza de validación
                self._generate_validation_trace()
            else:
                self.validation_trace.append("Paso 1: Se intentó buscar el patrón en el texto. No se encontró ninguna coincidencia.")

            return True
        except re.error as e:
            # Capturar errores si el patrón regex es inválido
            self.explanations.append(f"Error en el patrón de expresión regular: {e}")
            self.validation_trace.append(f"Error en el patrón de expresión regular: {e}. No se pudo realizar la validación.")
            self.match = None # Asegurarse de que no haya coincidencia si hay un error en el patrón
            return False

    def get_full_match_info(self) -> dict:
        """
        Obtiene información sobre la coincidencia completa, si existe.

        Returns:
            dict: Un diccionario con 'found' (bool), 'match_string' (str),
                  'start_index' (int), 'end_index' (int).
                  'found' será False si no hay coincidencia.
        """
        if self.match:
            return {
                "found": True,
                "match_string": self.match.group(0),
                "start_index": self.match.start(),
                "end_index": self.match.end()
            }
        else:
            return {"found": False}

    def get_group_matches_info(self) -> list:
        """
        Obtiene información sobre los grupos capturados, si existen.
        Esta función se mantiene en la lógica aunque la GUI ya no los muestre,
        ya que la traza de validación aún puede hacer referencia a ellos.

        Returns:
            list: Una lista de diccionarios, cada uno con 'group_number' (int),
                  'match_string' (str), 'start_index' (int), 'end_index' (int).
                  Retorna una lista vacía si no hay grupos capturados o no hay coincidencia.
        """
        if self.match:
            groups = []
            # Iterar sobre todos los grupos capturados (empezando por el grupo 1)
            for i in range(1, (self.match.lastindex or 0) + 1):
                groups.append({
                    "group_number": i,
                    "match_string": self.match.group(i),
                    "start_index": self.match.start(i),
                    "end_index": self.match.end(i)
                })
            return groups
        return []

    def get_step_by_step_explanations(self) -> list:
        """
        Retorna la lista de explicaciones paso a paso generadas para el patrón regex.

        Returns:
            list: Una lista de cadenas, cada una representando una explicación
                  de un componente del patrón.
        """
        return self.explanations

    def get_validation_trace(self) -> list:
        """
        Retorna la lista de pasos de la traza de validación.
        """
        return self.validation_trace

    def _generate_regex_explanations(self):
        """
        Analiza el patrón regex de forma simplificada y genera explicaciones
        para cada uno de sus componentes.
        Esta es una implementación rudimentaria y no un analizador de expresiones
        regulares completo o un motor de simulación de NFA/DFA.
        """
        components = self._parse_regex_components(self.pattern)
        for comp_type, comp_value in components:
            explanation = self._get_explanation_for_component(comp_type, comp_value)
            self.explanations.append(explanation)

    def _generate_validation_trace(self):
        """
        Genera una traza simplificada de cómo la expresión regular validó el texto,
        enfocándose en la coincidencia completa y los grupos capturados.
        """
        self.validation_trace.append("--- Traza de Validación del Texto ---")
        if self.match:
            full_match_string = self.match.group(0)
            start_idx = self.match.start()
            end_idx = self.match.end()

            self.validation_trace.append(
                f"Paso 1: Se inició la búsqueda del patrón '{self.pattern}' en la cadena de entrada."
            )
            self.validation_trace.append(
                f"Paso 2: Se encontró una coincidencia completa: '{full_match_string}' "
                f"desde el índice {start_idx} hasta el {end_idx-1} (parte de la cadena: '{self.text[start_idx:end_idx]}')."
            )

            # Iterar sobre los grupos capturados para detallar la validación
            if self.match.lastindex:
                for i in range(1, self.match.lastindex + 1):
                    group_string = self.match.group(i)
                    group_start = self.match.start(i)
                    group_end = self.match.end(i)
                    self.validation_trace.append(
                        f"Paso {i+2}: El Grupo {i} del patrón coincidió con: '{group_string}' "
                        f"desde el índice {group_start} hasta el {group_end-1}."
                    )
            else:
                self.validation_trace.append(
                    "Paso 3: El patrón no contiene grupos de captura, o no se capturaron grupos en esta coincidencia."
                )
            self.validation_trace.append("Validación finalizada.")
        else:
            self.validation_trace.append("Paso 1: No se encontró ninguna coincidencia del patrón en la cadena de entrada.")


    def _parse_regex_components(self, pattern: str) -> list:
        """
        Intenta parsear el patrón regex en componentes básicos.
        Esta función es una simplificación y podría no manejar todos los casos
        complejos de expresiones regulares.

        Args:
            pattern (str): El patrón regex a parsear.

        Returns:
            list: Una lista de tuplas (tipo_componente, valor_componente).
        """
        components = []
        i = 0
        while i < len(pattern):
            char = pattern[i]
            if char == '\\':
                if i + 1 < len(pattern):
                    next_char = pattern[i+1]
                    # Metacarácteres de clase de caracteres o anclas especiales
                    if next_char in 'dwsDSWbBAZ':
                        components.append(('metacharacter', f'\\{next_char}'))
                        i += 2
                    elif next_char.isdigit(): # Referencias inversas como \1
                        components.append(('backreference', f'\\{next_char}'))
                        i += 2
                    else: # Carácter escapado (ej. \., \*, \[)
                        components.append(('literal', f'\\{next_char}'))
                        i += 2
                else: # Barra invertida al final de la cadena
                    components.append(('literal', '\\'))
                    i += 1
            elif char == '.':
                components.append(('dot', '.'))
                i += 1
            elif char in '*+?':
                # Si hay un cuantificador, se asocia con el último componente.
                # Esta lógica es simple y puede no manejar cuantificadores complejos
                # o mal ubicados.
                if components and components[-1][0] not in ('quantifier', 'quantified'):
                    last_comp_type, last_comp_value = components[-1]
                    components[-1] = ('quantified', (last_comp_type, last_comp_value, char))
                else:
                    # Cuantificador sin un elemento previo válido (ej. *abc)
                    components.append(('quantifier', char))
                i += 1
            elif char == '{':
                # Cuantificadores con llaves {n}, {n,}, {n,m}
                j = pattern.find('}', i)
                if j != -1:
                    quantifier_content = pattern[i:j+1]
                    if components and components[-1][0] not in ('quantifier', 'quantified'):
                        last_comp_type, last_comp_value = components[-1]
                        components[-1] = ('quantified', (last_comp_type, last_comp_value, quantifier_content))
                    else:
                        components.append(('quantifier', quantifier_content))
                    i = j + 1
                else: # Llave de apertura sin cerrar
                    components.append(('literal', char))
                    i += 1
            elif char == '[':
                # Conjunto de caracteres
                j = pattern.find(']', i)
                if j != -1:
                    char_set = pattern[i:j+1]
                    components.append(('char_set', char_set))
                    i = j + 1
                else: # Corchete de apertura sin cerrar
                    components.append(('literal', char))
                    i += 1
            elif char == '(':
                # Grupos (simplificado: busca el primer ')' de cierre)
                # No maneja grupos anidados o no de captura directamente en el parsing.
                group_start = i
                open_parens = 1
                j = i + 1
                while j < len(pattern) and open_parens > 0:
                    if pattern[j] == '(':
                        open_parens += 1
                    elif pattern[j] == ')':
                        open_parens -= 1
                    j += 1

                if open_parens == 0:
                    group_content = pattern[group_start:j]
                    components.append(('group', group_content))
                    i = j
                else: # Paréntesis de apertura sin cerrar
                    components.append(('literal', char))
                    i += 1
            elif char == '|':
                components.append(('or_operator', '|'))
                i += 1
            elif char == '^':
                components.append(('anchor', '^'))
                i += 1
            elif char == '$':
                components.append(('anchor', '$'))
                i += 1
            else:
                # Carácter literal
                components.append(('literal', char))
                i += 1
        return components

    def _get_explanation_for_component(self, comp_type: str, comp_value: any) -> str:
        """
        Retorna una explicación textual para un tipo de componente regex dado.

        Args:
            comp_type (str): El tipo de componente (ej. 'literal', 'metacharacter').
            comp_value (any): El valor del componente (ej. 'a', '\\d', '[abc]').

        Returns:
            str: Una cadena explicando el componente.
        """
        if comp_type == 'literal':
            return f"Literal: El carácter '{comp_value}' busca una coincidencia exacta con '{comp_value}' en el texto."
        elif comp_type == 'metacharacter':
            if comp_value == '\\d':
                return "Metacarácter '\\d': Coincide con cualquier dígito (0-9)."
            elif comp_value == '\\D':
                return "Metacarácter '\\D': Coincide con cualquier carácter que NO sea un dígito."
            elif comp_value == '\\w':
                return "Metacarácter '\\w': Coincide con cualquier carácter de 'palabra' (letras, números, guiones bajos)."
            elif comp_value == '\\W':
                return "Metacarácter '\\W': Coincide con cualquier carácter que NO sea de 'palabra'."
            elif comp_value == '\\s':
                return "Metacarácter '\\s': Coincide con cualquier carácter de espacio en blanco (espacio, tabulador, salto de línea, etc.)."
            elif comp_value == '\\S':
                return "Metacarácter '\\S': Coincide con cualquier carácter que NO sea un espacio en blanco."
            elif comp_value == '\\b':
                return "Metacarácter '\\b': Coincide con un 'límite de palabra' (transición entre carácter de palabra y no palabra)."
            elif comp_value == '\\B':
                return "Metacarácter '\\B': Coincide con un 'no límite de palabra' (dentro de una palabra o entre dos no palabras)."
            elif comp_value == '\\A':
                return "Ancla '\\A': Coincide solo al principio de la cadena (independiente de líneas múltiples)."
            elif comp_value == '\\Z':
                return "Ancla '\\Z': Coincide solo al final de la cadena (antes del salto de línea final opcional)."
            else:
                return f"Metacarácter: '{comp_value}'."
        elif comp_type == 'dot':
            return "Punto '.': Coincide con cualquier carácter individual (excepto el carácter de salto de línea por defecto)."
        elif comp_type == 'quantifier':
            if comp_value == '*':
                return "Cuantificador '*': Coincide con CERO o MÁS repeticiones del elemento anterior (codicioso por defecto)."
            elif comp_value == '+':
                return "Cuantificador '+': Coincide con UNA o MÁS repeticiones del elemento anterior (codicioso por defecto)."
            elif comp_value == '?':
                return "Cuantificador '?': Coincide con CERO o UNA repetición del elemento anterior (hace el elemento OPCIONAL)."
            elif comp_value.startswith('{') and comp_value.endswith('}'):
                content = comp_value[1:-1]
                if ',' in content:
                    parts = content.split(',')
                    min_val = parts[0]
                    max_val = parts[1] if len(parts) > 1 and parts[1] else 'infinitas'
                    if max_val == 'infinitas':
                         return f"Cuantificador '{comp_value}': Coincide con {min_val} o más repeticiones del elemento anterior."
                    else:
                        return f"Cuantificador '{comp_value}': Coincide con un mínimo de {min_val} y un máximo de {max_val} repeticiones del elemento anterior."
                else:
                    return f"Cuantificador '{comp_value}': Coincide con EXACTAMENTE {content} repeticiones del elemento anterior."
            return f"Cuantificador: '{comp_value}'."
        elif comp_type == 'quantified':
            original_type, original_value, quantifier = comp_value
            base_explanation = self._get_explanation_for_component(original_type, original_value)
            quantifier_explanation = self._get_explanation_for_component('quantifier', quantifier)
            return f"{base_explanation} {quantifier_explanation.replace('Cuantificador', 'Aplicado con el cuantificador')}"
        elif comp_type == 'char_set':
            if comp_value.startswith('[^'):
                return f"Conjunto de caracteres negado '{comp_value}': Coincide con CUALQUIER carácter que NO esté dentro de los corchetes."
            return f"Conjunto de caracteres '{comp_value}': Coincide con CUALQUIER carácter que esté dentro de los corchetes (ej. rango, lista de caracteres)."
        elif comp_type == 'group':
            return f"Grupo capturador '{comp_value}': Encierra una subexpresión y 'captura' el texto que coincide con ella."
        elif comp_type == 'or_operator':
            return "Operador 'O' '|': Coincide con la expresión regular que está A LA IZQUIERDA O la expresión regular que está A LA DERECHA de este operador."
        elif comp_type == 'anchor':
            if comp_value == '^':
                return "Ancla '^': Coincide con el INICIO de la cadena (o el inicio de una línea en modo multilínea)."
            elif comp_value == '$':
                return "Ancla '$': Coincide con el FINAL de la cadena (o el final de una línea en modo multilínea)."
            return f"Ancla: '{comp_value}'."
        elif comp_type == 'backreference':
            group_num = comp_value[1:]
            return f"Referencia inversa '{comp_value}': Coincide con el texto EXACTO que fue previamente capturado por el Grupo {group_num}."
        return f"Componente desconocido: {comp_value}"