import tkinter as tk
from tkinter import messagebox, filedialog
import re
import os


class MiAplicacionCompilador:

    def __init__(self):
        # objeto para ventana
        self.ventana = tk.Tk()

        self.inicializar_archivo_simbolos()

        # nombre ventana
        self.ventana.title("CODEMODE")
        self.ventana.geometry("800x800")
        # interfaz del programa
        self.crear_interfaz()
        # colores de palabras reseervadas
        self.iluminador_automatico()

    def inicializar_archivo_simbolos(self):
        # Crea el archivo y guarda la palabra reservada secuencialmente
        with open("Tabla de símbolos.txt", "w", encoding="utf-8") as archivo:
            archivo.write("RESERVADA,pantalla\n")

    def agregar_a_tabla(self, tipo, lexema, valor=None):
        # Agrega tokens o valores al final del archivo.
        # (Se cambió a 'valor is not None' para aceptar strings vacíos "")
        with open("Tabla de símbolos.txt", "a", encoding="utf-8") as archivo:
            if valor is not None:
                archivo.write(f"{tipo},{lexema},{valor}\n")
            else:
                archivo.write(f"{tipo},{lexema}\n")

    def obtener_valor_variable(self, nombre_var):
        # Lee el archivo de abajo hacia arriba para encontrar el último valor asignado
        if not os.path.exists("Tabla de símbolos.txt"):
            return None
        with open("Tabla de símbolos.txt", "r", encoding="utf-8") as archivo:
            lineas = archivo.readlines()

        for linea in reversed(lineas):
            # split(',', 2) para no romper strings que contengan comas
            datos = linea.strip().split(',', 2)
            if len(datos) >= 3 and datos[0] == "VALOR" and datos[1] == nombre_var:
                val_str = datos[2]
                try:
                    return float(val_str) if '.' in val_str else int(val_str)
                except ValueError:
                    return val_str
        return None

    def crear_interfaz(self):
        self.frame_botones = tk.Frame(self.ventana)
        self.frame_botones.pack(pady=10)
        ###################  Botones  ####################
        # boton de abrir archivos
        tk.Button(self.frame_botones, text="Abrir Archivo", command=self.abrir_archivo, width=15).pack(side=tk.LEFT,
                                                                                                       padx=5)
        # boton compilar
        tk.Button(self.frame_botones, text="Compilar", command=self.compilador_visual, width=15).pack(side=tk.LEFT,
                                                                                                      padx=5)
        # boton limpiar txt
        tk.Button(self.frame_botones, text="Limpiar", command=self.limpiar_pantallas, width=15).pack(side=tk.LEFT,
                                                                                                     padx=5)
        # boton Correr programas
        tk.Button(self.frame_botones, text="Correr", command=self.correr, width=15).pack(side=tk.LEFT, padx=5)

        # caja Area de codigo
        self.caja_texto = tk.Text(self.ventana, height=20, width=80, font=("Consolas", 12))
        self.caja_texto.pack(pady=5)

        # configuracion de colores de texto
        self.caja_texto.tag_config("instrucciones", foreground="blue", font=("Consolas", 12, "bold"))
        self.caja_texto.tag_config("variable", foreground="#BE4BDB", font=("Consolas", 12, "bold"))
        self.caja_texto.tag_config("string", foreground="#41AF39")
        self.caja_texto.tag_config("operador", foreground="orange")
        self.caja_texto.tag_config("numero", foreground="#FF0000")

        self.consola_salida = tk.Text(self.ventana, height=22, width=80, bg="#333333", state="disabled",
                                      font=("Consolas", 12))
        self.consola_salida.pack(pady=5)
        self.consola_salida.tag_config("verde", foreground="#00FF00")
        self.consola_salida.tag_config("rojo", foreground="#FF3333")

    def iluminador_automatico(self):
        # Limpiar coloreas antes de pintar
        for tag in ["instrucciones", "variable", "string", "operador", "numero"]:
            self.caja_texto.tag_remove(tag, "1.0", tk.END)

        # Colorear letras
        patrones = [(r'pantalla', "instrucciones"), (r'#.*?#', "variable"), (r'".*?"', "string"),
                    (r'\[.*?\]', "numero"),
                    (r'[+\-*/=]', "operador")]

        for pattern, tag in patrones:
            inicio = "1.0"
            while True:
                count = tk.IntVar()
                pos = self.caja_texto.search(pattern, inicio, stopindex=tk.END, regexp=True, count=count)

                # Verificar longitud de la cadeta
                if not pos or count.get() == 0:
                    break

                # Calcular el final exacto usando la longitud encontrada (count)
                fin = f"{pos}+{count.get()}c"
                self.caja_texto.tag_add(tag, pos, fin)

                # Cambiar inicio de la cadena a colorear
                inicio = fin
        # Ejecutar cada 3 segundos el metodo
        self.ventana.after(1000, self.iluminador_automatico)

    def separar_instrucciones(self, texto):
        # guardar instrucciones
        instrucciones = []
        inicio = 0
        i = 0
        # tamaño texto
        longitud = len(texto)
        dentro_string = False
        # recorrer toda la longitud del codigo
        while i < longitud:
            # analizar caracter
            caracter = texto[i]
            if caracter == '"':
                dentro_string = not dentro_string
            # Fin de la instruccion
            if caracter == ';' and not dentro_string:
                inst = texto[inicio:i].strip()
                if inst:
                    # agregar instruccion a lista de instrucciones
                    instrucciones.append(inst)
                inicio = i + 1
            i += 1
        # Recorrer instrucciones para analizar
        if inicio < longitud:
            inst = texto[inicio:].strip()
            if inst:
                instrucciones.append(inst)

        return instrucciones

    def validar_contenido_pantalla(self, tokens, n_linea):
        # no hay tokens a analizar
        if not tokens:
            return True
        # para cada token recorrer
        for token in tokens:
            # token de texto
            if token.startswith('"') and token.endswith('"'):
                continue
            # token de variable
            elif token.startswith('#') and token.endswith('#'):
                nombre_var = token[1:-1]
                # validar nombre de variable entre ##
                if not nombre_var or not all(c.isalnum() or c == '_' for c in nombre_var):
                    self.escribir_en_consola(f"Error linea [{n_linea}]: Variable invalida {token}", "rojo")
                    return False
                continue
            # verificar dato detnro de corchetes []
            elif token.startswith('[') and token.endswith(']'):
                num_str = token[1:-1]
                try:
                    float(num_str)
                    continue
                except:
                    self.escribir_en_consola(f"Error linea [{n_linea}]:Numero inválido {token}", "rojo")
                    return False
            elif token == '+':
                continue
            else:
                self.escribir_en_consola(f"Error linea [{n_linea}]: {token} No aceptado en instruccion pantalla()",
                                         "rojo")
                return False
        return True

    def validar_instruccion_pantalla(self, tokens, n_linea):
        # Cadena minima en pantalla
        if len(tokens) < 3:
            self.escribir_en_consola(f"Error linea [{n_linea}]: Instrucción pantalla() incompleta.", "rojo")
            return False

        # Verificar que comience con "pantalla"
        if tokens[0] != 'pantalla':
            self.escribir_en_consola(f"Error linea [{n_linea}]: La instrucción debe comenzar con 'pantalla'.", "rojo")
            return False

        # Verificar que el siguiente token sea "("
        if len(tokens) < 2 or tokens[1] != '(':
            self.escribir_en_consola(f"Error linea [{n_linea}]: Se esperaba '(' después de pantalla.", "rojo")
            return False

        # Encontrar el paréntesis ")" de cierre
        idx_close = -1
        for j, token in enumerate(tokens):
            if token == ')':
                idx_close = j
                break

        if idx_close == -1:
            self.escribir_en_consola(f"Error linea [{n_linea}]: Cierre ')' no encontrado", "rojo")
            return False

        # Verificar que después de ')' no haya más tokens (excepto si es el final)
        if idx_close + 1 < len(tokens):
            self.escribir_en_consola(
                f"Error linea [{n_linea}]: (;) no encontrado: no aceptado ({tokens[idx_close + 1]})", "rojo")
            return False

        # Verificar que no haya otro comando dentro de pantalla
        contenido_tokens = tokens[2:idx_close]
        if 'pantalla' in contenido_tokens:
            self.escribir_en_consola(f"Error linea [{n_linea}]: Instruccion invalida", "rojo")
            return False

        return True

    def automata(self, texto):
        # Aqui se guardaran los tokens
        tokens = []
        i = 0
        n = len(texto)  # largo del codigo

        while i < n:
            caracter = texto[i]

            # ignorar espacios
            if caracter.isspace():
                i += 1
                continue

            # valores con corchetes [ ]
            if caracter == '[':
                inicio = i
                i += 1
                encontrado = False
                while i < n:
                    if texto[i] == ']':
                        encontrado = True
                        break
                    i += 1
                if encontrado:
                    token = texto[inicio:i + 1]
                    num_str = token[1:-1]
                    try:
                        float(num_str)
                        tokens.append(token)
                        self.agregar_a_tabla("DIGITO", token)
                    except:
                        raise SyntaxError(f"Número inválido: {token}")
                    i += 1
                else:
                    raise SyntaxError("Corchete de cierre ']' no encontrado")
                continue

            # Variables entre ##
            if caracter == '#':
                inicio = i
                i += 1
                if i < n and texto[i] == '#':
                    raise SyntaxError("Nombre de variable vacío (##) no permitido")

                encontrado = False
                while i < n:
                    if texto[i] == '#':
                        encontrado = True
                        break
                    i += 1

                if encontrado:
                    nombre_var = texto[inicio:i + 1]
                    nombre_limpio = nombre_var[1:-1]
                    if not nombre_limpio:
                        raise SyntaxError("Nombre de variable vacio no permitido")
                    if not all(c.isalnum() or c == '_' for c in nombre_limpio):
                        raise SyntaxError(f"Nombre de variable invalido: {nombre_var}")
                    tokens.append(nombre_var)
                    self.agregar_a_tabla("IDENTIFICADOR", nombre_var)
                    i += 1
                else:
                    raise SyntaxError("Cierre '#' no encontrado para variable")
                continue

            # Strings entre comillas
            if caracter == '"':
                inicio = i
                i += 1
                encontrado = False
                while i < n:
                    if texto[i] == '"':
                        encontrado = True
                        break
                    i += 1
                if encontrado:
                    tokens.append(texto[inicio:i + 1])
                    i += 1
                else:
                    raise SyntaxError("Comillas de cierre no encontradas")
                continue

            # Operadores
            if caracter in '+-*/=();':
                tokens.append(caracter)
                i += 1
                continue

            # Palabras clave (solo pantalla)
            if caracter.isalpha():
                inicio = i
                while i < n and (texto[i].isalpha() or texto[i].isdigit()):
                    i += 1
                palabra = texto[inicio:i]
                if palabra == 'pantalla':
                    tokens.append(palabra)
                else:
                    raise SyntaxError(f"Palabra no reconocida: '{palabra}'")
                continue

            raise SyntaxError(f"Carácter no válido: '{caracter}'")

        return tokens

    def obtener_valor_unidad(self, token, n_linea):
        # Para variables
        if token.startswith("#") and token.endswith("#"):
            var_name = token[1:-1]
            if not var_name:
                self.escribir_en_consola(f"Error linea [{n_linea}]: (##) no permitido.", "rojo")
                return None

            valor = self.obtener_valor_variable(var_name)

            if valor is None:
                self.escribir_en_consola(f"Error linea [{n_linea}]: Variable '{token}' no encontrada", "rojo")
            return valor

        # Cadena de texto sin ""
        if token.startswith('"') and token.endswith('"'):
            return token[1:-1]
        # valor numerico sin []
        if token.startswith("[") and token.endswith("]"):
            num_str = token[1:-1].strip()
            try:
                if '.' in num_str:
                    return float(num_str)
                else:
                    return int(num_str)
            except ValueError:
                self.escribir_en_consola(f"Error linea [{n_linea}]:Numero invalido '{num_str}'.", "rojo")
                return None

        self.escribir_en_consola(f"Error linea [{n_linea}]: Token invalido  '{token}'.", "rojo")
        return None

    def evaluar_expresion(self, tokens, n_linea, es_pantalla=False):
        # Evaluar si hay tokens
        if not tokens:
            return None

        if es_pantalla:
            # Verificar concatenacion en instruccion operacion
            for token in tokens:
                if token in '-*/':
                    self.escribir_en_consola(f"Error linea [{n_linea}]: Operador '{token}' no permitido", "rojo")
                    return None

        # Extraer valores y operadores
        valores = []
        operadores = []

        for token in tokens:
            if token in '+-*/':
                operadores.append(token)
            else:
                valor = self.obtener_valor_unidad(token, n_linea)
                if valor is None:
                    return None
                valores.append(valor)

        if len(valores) != len(operadores) + 1:
            self.escribir_en_consola(f"Error linea [{n_linea}]: Expresión inválida.", "rojo")
            return None

        # Expreciones
        expr = []
        for i in range(len(valores)):
            expr.append(valores[i])
            if i < len(operadores):
                expr.append(operadores[i])

        # procesar operadores
        i = 1
        while i < len(expr):
            if expr[i] in '*/':
                izquierdo = expr[i - 1]
                derecho = expr[i + 1]
                operador = expr[i]

                # verificar cadenas
                if isinstance(izquierdo, str) or isinstance(derecho, str):
                    if operador == '*':
                        try:
                            if isinstance(izquierdo, str) and isinstance(derecho, (int, float)):
                                resultado = izquierdo * int(derecho)
                            elif isinstance(derecho, str) and isinstance(izquierdo, (int, float)):
                                resultado = derecho * int(izquierdo)
                            else:
                                resultado = str(izquierdo) + str(derecho)
                        except:
                            resultado = str(izquierdo) + str(derecho)
                    else:
                        resultado = str(izquierdo) + str(derecho)
                else:
                    if operador == '*':
                        resultado = izquierdo * derecho
                    elif operador == '/':
                        if derecho == 0:
                            self.escribir_en_consola(f"Error linea [{n_linea}]: division entre cero.", "rojo")
                            return None
                        resultado = izquierdo / derecho

                expr[i - 1] = resultado
                expr.pop(i)
                expr.pop(i)
            else:
                i += 2

        # evaluar + y -
        resultado = expr[0]
        i = 1
        while i < len(expr):
            operador = expr[i]
            derecho = expr[i + 1]

            # EL ARREGLO ESTÁ AQUÍ: Si es pantalla, obliga a que lo trate como texto.
            if es_pantalla or isinstance(resultado, str) or isinstance(derecho, str):
                if operador == '+':
                    resultado = str(resultado) + str(derecho)
                elif operador == '-':
                    resultado = str(resultado) + str(derecho)
                else:
                    resultado = str(resultado) + str(derecho)
            else:
                if operador == '+':
                    resultado = resultado + derecho
                elif operador == '-':
                    resultado = resultado - derecho

            i += 2

        return resultado

    def compilar(self, ejecutar=False):
        codigo = self.caja_texto.get("1.0", tk.END).strip()
        self.inicializar_archivo_simbolos()

        if not codigo:
            return False

        # EL ARREGLO ESTÁ AQUÍ: Comprueba que el código en general termine en punto y coma.
        if not codigo.endswith(';'):
            self.escribir_en_consola("Error de sintaxis: Falta punto y coma (;) al final del código.", "rojo")
            return False

        # primero separar instrucciones
        instrucciones = self.separar_instrucciones(codigo)

        # buscar error de gramatica en isntrucciones
        for i, instruccion in enumerate(instrucciones):
            n_linea = i + 1

            try:
                tokens = self.automata(instruccion)
            except SyntaxError as e:
                self.escribir_en_consola(f"Error linea [{n_linea}]: {str(e)}", "rojo")
                return False

            # Salir del ciclo si ya no existen tokens
            if not tokens:
                continue

            # tipo asignacion
            if "=" in tokens:
                # Asignacion de variable
                idx_igual = -1
                for j, token in enumerate(tokens):
                    if token == "=":
                        idx_igual = j
                        break

                if idx_igual == -1 or idx_igual == 0:
                    self.escribir_en_consola(f"Error linea [{n_linea}]:No se pudo asignar valor.", "rojo")
                    return False

                # evaluar nombre de variable
                var_token = tokens[idx_igual - 1]
                if not (var_token.startswith("#") and var_token.endswith("#")):
                    self.escribir_en_consola(f"Error linea [{n_linea}]:Gramatica de variable invalida", "rojo")
                    return False

                # nombre variable vacio
                var_name = var_token[1:-1]
                if not var_name:
                    self.escribir_en_consola(
                        f"Error linea [{n_linea}]:Gramatica de variable invalida, variable vacia (##) no permitido.",
                        "rojo")
                    return False

                # valor de asigancion o exprecion
                expr_tokens = tokens[idx_igual + 1:]
                resultado = self.evaluar_expresion(expr_tokens, n_linea, es_pantalla=False)

                if resultado is not None:
                    self.agregar_a_tabla("VALOR", var_name, resultado)
                else:
                    return False

            ############# INSTRUCCIONES #########################
            elif tokens and tokens[0] == "pantalla":
                # validar instruccion pantalla
                if not self.validar_instruccion_pantalla(tokens, n_linea):
                    return False

                # Encontrar parentesis
                idx_open = 1
                idx_close = -1
                for j, token in enumerate(tokens):
                    if token == ')':
                        idx_close = j
                        break

                if idx_close == -1:
                    return False

                if idx_close == idx_open + 1:
                    # pantalla() vacia no escribe nada
                    if ejecutar:
                        self.escribir_en_consola("", "verde")
                else:
                    inner_tokens = tokens[idx_open + 1:idx_close]
                    # validar contenido de pantalla
                    if not self.validar_contenido_pantalla(inner_tokens, n_linea):
                        return False

                    resultado = self.evaluar_expresion(inner_tokens, n_linea, es_pantalla=True)

                    if ejecutar and resultado is not None:
                        self.escribir_en_consola(str(resultado), "verde")
                    elif resultado is None:
                        return False
            else:
                self.escribir_en_consola(
                    f"Error linea [{n_linea}]: Instrucción no reconocida.", "rojo")
                return False
        # retornar true cuando es aceptado
        return True

    def escribir_en_consola(self, mensaje, color=None, limpiar=False):
        self.consola_salida.config(state="normal")
        if limpiar:
            self.consola_salida.delete("1.0", tk.END)
        if mensaje:
            self.consola_salida.insert(tk.END, mensaje + "\n", color)
        self.consola_salida.config(state="disabled")  # Desabilitar txt para evitar edicion
        self.consola_salida.see(tk.END)

    def abrir_archivo(self):
        ruta = filedialog.askopenfilename()
        if ruta:
            with open(ruta, 'r', encoding='utf-8') as archivo:
                # guardar contenido en variable contenido
                contenido = archivo.read()
                self.caja_texto.delete("1.0", tk.END)
                # mostrar en area de edicion de texto
                self.caja_texto.insert(tk.END, contenido)

    def correr(self):
        self.escribir_en_consola("", limpiar=True)
        self.compilar(ejecutar=True)

    def compilador_visual(self):
        self.escribir_en_consola("", limpiar=True)
        if self.compilar(ejecutar=False):
            self.escribir_en_consola("Gramatica aceptada", "verde")

    def limpiar_pantallas(self):
        self.caja_texto.delete("1.0", tk.END)
        self.escribir_en_consola("", limpiar=True)


if __name__ == "__main__":
    MiAplicacionCompilador().ventana.mainloop()