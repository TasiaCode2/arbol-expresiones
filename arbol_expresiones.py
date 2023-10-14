import re
import graphviz

exp = str(input("Ingrese la expresion matematica: "))
exp = convertir_a_parentesis(exp.replace(' ', ''))

while not (exp := validar_expresion(exp)):
  exp = str(input("Ingrese la expresion de nuevo: "))

arbol = calcular_arbol(exp)
arbol

def convertir_a_parentesis(exp):
  pattern1 = r'[\[\{]'
  pattern2 = r'[\]\}]'
  return re.sub(pattern2, ')', re.sub(pattern1, '(', exp))

def validar_expresion(exp):
  #print(exp, "----------------------------------------------------------------------------------------------------")
  pattern = r'^[a-zA-Z0-9\(\)\[\]\{\}\-\+\=\*\/]+$' # Para detectar cuando hay algun caracter prohibido
  pattern2 = r'[a-zA-Z0-9\(\)\[\]\{\}\-\+\=\*\/]'   # Para sustituir cada uno de los caracteres permitidos

  # Checar caracteres prohibidos
  if not (re.match(pattern, exp)):
    result_string = re.sub(pattern2, '', exp)
    print("La expresion contiene caracteres raros. Evite usar:", result_string)
    return False

  # Checar cantidad de parentesis
  cont_aper = exp.count('(')
  cont_cierre = exp.count(')')

  if (cont_aper != cont_cierre):
    print("Debe haber la misma cantidad de simbolos de cierre y apertura")
    return False

  # 2v -> 2 * v
  pattern3 = r"[0-9]+[a-zA-Z]"
  if re.search(pattern3, exp):
    print("Letras y números no deben ir juntos. Recuerda expresar valores como 2y o 3x como 2*y o 3*x")
    return False

  indices = set()
  parentesis = set()
  parentesis.add('(')
  parentesis.add(')')

  for idx, char in enumerate(exp):
    #print("Evaluando ", char, " en idx ", idx)
    if char == '+' or char == '/':                # Encontrar los operadores binarios (+/) y checar que a los lados tengan operandos
      if not validar_operador_binario(char, exp, idx):
        return False
    if char == '*':                               # checar los asteriscos
      if esta_entre_caracteres(idx, exp):
        if idx not in indices:             # si no es un indice que ya revisamos
          if exp[idx+1] == '*':                              # evaluamos si es un doble **
            if esta_entre_caracteres(idx + 2, exp):
              if exp[idx-1].isdigit() and exp[idx + 2].isdigit():     # checa que el ** este rodeado de numeros
                indices.add(idx + 1)                                  # agregamos el indice del segundo * para no volverlo a evaluar
              else:
                print("Hay un signo binario '**' que le falta un operando")
                return False
            else:
                print("Hay un signo binario '**' que le falta un operando")
                return False
          else:
            if validar_operador_binario(char, exp, idx) == False:  # si no es un doble **, evaluamos que el * tenga operandos
              return False
      else:
        print("Hay un signo binario '*' que le falta un operando")
        return False # no esta entre caracteres
    if char in parentesis:
      if validar_parentesis(idx, exp) == False:
        print("Hay un simbolo '", char, "' que le falta un operando", sep='')
        return False
    # checar el signo - (ese puede ser unitario)
  #print("Esta al 100!")
  return exp

def validar_operador_binario(char, exp, idx):
  if esta_entre_caracteres(idx, exp):           # si hay caracteres a la derecha e izquierda
    if not esta_entre_operandos(exp, idx):      # checa que sean numeros o variables
      print("Hay un signo binario '", char, "' que le falta un operando", sep='')
      return False
  else:
    print("Hay un signo binario '", char, "' que le falta un operando", sep='')
    return False
  return True

def esta_entre_caracteres(idx, exp):
  return idx - 1 >= 0 and idx + 1 <= len(exp)   # checa que los indices antes y despues del caracter, esten dentro del rango (o sea que el caracter analizandose no es ni el primero ni el ultimo)

def esta_entre_operandos(exp, idx):
  return (exp[idx-1].isdigit() or exp[idx-1].isalpha() or exp[idx-1] == ')') and (exp[idx+1].isdigit() or exp[idx+1].isalpha() or exp[idx+1] == '(')

def validar_parentesis(idx, exp):
  if idx + 1 <= len(exp) and exp[idx] == '(': # si es ()
    return not exp[idx + 1] == ')'            # y al lado tiene ), no es valido (devolvemos False)
  if idx + 1 <= len(exp) and exp[idx] == ')':
    return not exp[idx + 1] == '('
  return False
  
def crear_nodo(token, contador, dot, operadores_ref):
  style = "invis" if token == '(' else ""
  nombre_nodo = crear_nombre(token, contador)
  dot.node(name = nombre_nodo, label = token, style = style)

  if not (token.isdigit()) and not (token.isalpha()):
    operadores_ref[nombre_nodo] = token

  return nombre_nodo

def crear_nombre(token, contador):
  if(token.isdigit() or token.isalpha()):
    return "num" + (str(contador))

  return "op" + (str(contador))

def check_peek(op, operadores_ref):
  return operadores_ref[op[len(op) - 1]]

def calcular_arbol(exp):
  dot = graphviz.Digraph(comment='Arbol de expresiones')
  contador_op = 1
  contador_num = 1
  operadores = []
  operandos = []
  operadores_ref = {}
  presedencia = {"(": 4, ")": 4, "**": 3, "/": 2, "*": 2, "+": 1, "-": 1, "=": 0} # buscar como funcionan los diccionarios en python
  
  terminos = exp.split("=")
  dot.node('I', '=')
  dot.node('S', terminos[0])
  tokens = [i for i in re.split(r'(\*\*|\d+\.\d+|\d+|\D)', terminos[1]) if i] # los -2 como un solo nodo
  
  for token in tokens:              # Para cada token en la lista de tokens
    #print("Analizando", token)
    #print(dot.source)
    if (token.isdigit() or token.isalpha()):
      operandos.append(crear_nodo(token, contador_num, dot, operadores_ref))           # crea un nodo hoja con ese número y colócalo en la pila de operandos.
      contador_num = contador_num + 1
      continue;

    # Si el token es un paréntesis izquierdo
    if (token == '('):    
      operadores.append(crear_nodo(token, contador_op, dot, operadores_ref))          # colócalo en la pila de operadores.
      contador_op = contador_op + 1
      continue;

    # Si el token es un paréntesis derecho
    if (token == ')'):                          
      while(check_peek(operadores, operadores_ref) != '('):         # Mientras el operador en la parte superior de la pila de operadores no sea un paréntesis izquierdo:
        # todos estos ya son nodos
        operador = operadores.pop()
        operando1 = operandos.pop()
        operando2 = operandos.pop()
        dot.edge(operador, operando1)
        dot.edge(operador, operando2)
        operandos.append(operador)                                  # guardar como operandos

      # fuera del while
      operadores.pop()                  # Pop el paréntesis izquierdo de la pila de operadores.
      continue;

    # Si el token es un operador
    else:
      while(len(operadores) > 0 and operadores_ref[operadores[len(operadores) - 1]] != '(' and presedencia[operadores_ref[operadores[len(operadores) - 1]]] >= presedencia[token]):    # Mientras la pila de operadores no esté vacía y el operador en la parte superior tenga mayor o igual precedencia que el token:
        # ya son nodos
        operador = operadores.pop()  # Pop el operador de la pila de operadores.
        num1 = operandos.pop()
        num2 = operandos.pop()
        dot.edge(operador, num1)
        dot.edge(operador, num2)
        operandos.append(operador)   # Empuja el token actual en la pila de operadores.
      
      operadores.append(crear_nodo(token, contador_op, dot, operadores_ref))
      contador_op = contador_op + 1
  
  # Terminar de hacer uniones
  while(len(operadores) > 0 and operadores_ref[operadores[len(operadores) - 1]] != '('):
    operando1 = operandos.pop()
    operando2 = operandos.pop()
    operador = operadores.pop()
    dot.edge(operador, operando1)
    dot.edge(operador, operando2)
    operandos.append(operador)

  # Unir todo con el signo de =
  dot.edge('I','S')
  dot.edge('I', operandos.pop())
  return dot