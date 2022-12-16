from enum import Enum
#Cada tipo tiene asignada un booleano que indica si puede tener mas instrucciones dentro o no
class TipoInstruccion(Enum):
    #Instrucciones que NO pueden tener mas instrucciones anidadas 0-6
    DeclaracionVariable = 0
    LlamadaFuncion = 1
    Asignacion = 2
    Continue = 3
    Break = 4
    Return = 5
    Print = 6
    
    #Instrucciones que pueden tener mas instrucciones anidadas 7-11
    DeclaracionFuncion = 7,
    If = 8                     #Si puede tener al final del todo una instruccion SINO
    Else = 9                   #Solo puede existir una instruccion Else si esta complementa una instruccion If
    Elif = 10                   #Solo puede existir una instruccion Else si esta complementa una instruccion If-Elif
    While = 11
    For = 12
    
    DeclaracionStruct = 13

class TipoNoTerminal(Enum):
    Parametros = 0    
    Identificadores = 1
    DeclaracionParametro = 2
    DeclaracionParametros = 3
    CondicionInicialPara = 4
    
    Instrucciones = 5
    
    ParametrosMostrar = 6
    IndiceLista = 7
    DeclaracionLista = 8
    LlamadaMetodo = 9
    CamposStruct = 10
    Atributo = 11

class TipoExpresionMatematica(Enum):
    Suma="SUMA",                        #Se espera -> expresion SUMA expresion
    Resta="RESTA",                      #Se espera -> expresion RESTA expresion
    Multiplicacion="MULTIPLICACION",    #Se espera -> expresion MULTIPLICACION expresion
    Division="DIVISION",                #Se espera -> expresion DIVISION expresion
    Modulo="MODULO",                    #Se espera -> expresion MODULO expresion
    Potencia="POTENCIA",                #Se espera -> expresion POTENCIA expresion
    MenosUnitario="MENOS_U",            #Se espera -> MENOS_U expresion
    Grupo="GRUPO"                       #Se espera -> PAR_IZQ expresion PAR_DER

class TipoExpresionRelacional(Enum):
    MayorQue="MAYOR_QUE",               #Se espera -> expresion MAYOR_QUE expresion
    MenorQue="MENOR_QUE",               #Se espera -> expresion MENOR_QUE expresion
    MayorIgualQue="MAYOR_IGUAL_QUE",    #Se espera -> expresion MAYOR_IGUAL_QUE expresion
    MenorIgualQue="MENOR_IGUAL_QUE",    #Se espera -> expresion MENOR_IGUAL_QUE expresion
    Igualdad="IGUALDAD",                #Se espera -> expresion IGUALDAD expresion
    Diferencia="DIFERENCIA",            #Se espera -> expresion DIFERENCIA expresion

class TipoExpresionLogica(Enum):
    And="AND",      #Se espera -> expresion AND expresion
    Or="OR",        #Se espera -> expresion OR expresion
    Not="NOT"       #Se espera -> NOT expresion

class TipoDato(Enum):
    Int = 0
    Float = 1
    String = 2
    Boolean = 3
    None_ = 4
    List = 5

class Token(object):
    lexema: str
    linea: int
    columna: int

    def __init__(self, lexema: str, linea: int, columna: int):
        self.lexema = lexema
        self.linea = linea
        self.columna = columna

    def __str__(self):
        return f"Token(Lexema:{self.lexema},Linea:{self.linea},Columna:{self.columna})"
    
class Terminal(object):
    token : any
    #: Token

    def __init__(self, token):
        self.token = token

    def __str__(self):
        return f"Terminal({self.token})"        

class TerminalTipoDato(Terminal):
    tipoDato: TipoDato

    def __init__(self, token: Token, tipoDato: TipoDato|Token):
        super().__init__(token)
        self.tipoDato = tipoDato;
    
    def __str__(self):
        return f"TerminalTipoDato({self.token},Tipo:{self.tipoDato})"

class Nodo(object):
    hijos = []
    
    def __init__(self):
        self.hijos = []

    def agregarhijo(self, hijo):
        self.hijos.append(hijo)
    
    def agregarhijos(self, hijos):
        for hijo in hijos:
            self.hijos.append(hijo)
        
class NodoRaiz(Nodo):
    pass

class NodoNoTerminal(Nodo):
    tipoNoTerminal: TipoNoTerminal;

    def __init__(self, tipoNoTerminal: TipoNoTerminal):
        super().__init__()
        self.tipoNoTerminal = tipoNoTerminal
        
    def __str__(self):
        string = f"{self.tipoNoTerminal}(\n"
        for hijo in self.hijos:
            string += str(hijo)+" "
        return string + "\n)"

class NodoInstruccion(Nodo):
    tipoInstruccion: TipoInstruccion

    def __init__(self, tipoInstruccion):
        super().__init__()
        self.tipoInstruccion = tipoInstruccion

    def __str__(self):
        string = f"{self.tipoInstruccion}(\n"
        for hijo in self.hijos:
            string += str(hijo)+" "
        return string + "\n)"

class NodoExpresion(Nodo):
    operador : TipoExpresionMatematica | TipoExpresionRelacional | TipoExpresionLogica
    #NodoExpresion | NodoNoTerminal | Terminal []
    
    def __init__(self, operador, expresiones ):
        super().__init__()
        self.operador = operador
        for expresion in expresiones:
            super().agregarhijo(expresion)
            

    def __str__(self):
        string = f"{self.operador}(\n"
        for hijo in self.hijos:
            string += str(hijo)+" "
        return string + "\n)"                             

def recorrer(ast: Nodo):
    # Se obtiene el tipo de nodo a recorrer
    
    if isinstance(ast, NodoInstruccion):                        #Si es un nodo de instruccion
        if ast.tipoInstruccion == TipoInstruccion.Asignacion:   #Asignacion espera -> id tipo? valor
            
            #Se comprueba si el primer hijo es un token
            if isinstance(ast.hijos[0], Token):
                #Se obtiene el id al que se quiere asignar
                id_var = ast.hijos[0].lexema
            elif isinstance(ast.hijos[0], Terminal):
                #Se obtiene el id al que se quiere asignar
                id_var = ast.hijos[0].token.lexema
            else:
                id_var = ast.hijos[0]                
            
            #Se verifica el tipo de dato a asignar
            if isinstance(ast.hijos[1], TipoDato):              #Se comprueba si el tipo fue indicado explicitamente
                tipo_var = ast.hijos[1]
                valor_var = ast.hijos[2]
            else:                                               #Si no esta explicitamente indicado explicitamente se obtiene el tipo del valor
                tipo_var = obtenerTipo(ast.hijos[1])
                valor_var = ast.hijos[1]
            
            #Se imprime la asignacion
            print("Asignacion-----------\n")
            print(id_var, "id\n")
            print(tipo_var, "tipo\n")
            print(valor_var, "valor\n")
            print("---------------------\n")
        elif ast.tipoInstruccion == TipoInstruccion.LlamadaFuncion: #LlamadaFunction espera -> id parametros
            id_func = ast.hijos[0].token.lexema

            parametros = ast.hijos[1]

            #Se imprime la llamada
            print("Llamada-------------\n")
            print(id_func, "id\n")
            #Se imprimen los parametros
            recorrer(parametros)
            #print(parametros, "parametros\n")
            print("---------------------\n")
        elif ast.tipoInstruccion == TipoInstruccion.DeclaracionFuncion: #DeclaracionFuncion espera -> id parametros instrucciones
            id_declar = ast.hijos[0].lexema
            parametros = ast.hijos[1]            
            instrucciones = ast.hijos[2]

            #Se imprime la definicion
            print("DefinicionFuncion----\n")
            print(id_declar, "id\n")

            #Se imprimen los parametros
            recorrer(parametros)
            #print(parametros, "parametros\n")

            print("---------------------\n")
        elif ast.tipoInstruccion == TipoInstruccion.If: #If espera -> condicion instrucciones (else | elif)?
            condicion = ast.hijos[0]

            instrucciones = ast.hijos[1]
            
            print("If-------------------\n")
            print("Condicion: ")
            recorrer(condicion)

            #Instrucciones
            #recorrer(instrucciones)
            #print(parametros, "parametros\n")

            #Se verifica si existe un else o elif en el if
            if len(ast.hijos) > 2:
                extension = ast.hijos[2]
                #Si ese es el caso se verifica si es un else o un elif
                if extension.tipoInstruccion == TipoInstruccion.Else:
                    print("Else:")
                    recorrer(extension)
                elif extension.tipoInstruccion == TipoInstruccion.Elif:
                    print("Elif:")
                    recorrer(extension)
            print("---------------------\n")
            
        elif ast.tipoInstruccion == TipoInstruccion.Else:   #Else espera -> Token(Else) instrucciones
            for hijo in ast.hijos:
                #recorrer(hijo)
                pass
        elif ast.tipoInstruccion == TipoInstruccion.Elif:   #Elif espera -> condicion instrucciones (else | elif)?
            condicion = ast.hijos[0]

            instrucciones = ast.hijos[1]
            
            print("Condicion: ")
            recorrer(condicion)

            #Instrucciones
            #recorrer(instrucciones)
            #print(parametros, "parametros\n")

            #Se verifica si existe un else o elif en el if
            if len(ast.hijos) > 2:
                extension = ast.hijos[2]
                #Si ese es el caso se verifica si es un else o un elif
                if extension.tipoInstruccion == TipoInstruccion.Else:
                    print("Else:")
                    recorrer(extension)
                elif extension.tipoInstruccion == TipoInstruccion.Elif:
                    print("Elif:")
                    recorrer(extension)

        elif ast.tipoInstruccion == TipoInstruccion.While:  #While espera -> condicion instrucciones
            condicion = ast.hijos[0]
            
            instrucciones = ast.hijos[1]

            print("While---------------\n")
            recorrer(condicion)
            
            #recorrer(instrucciones)

            print("---------------------\n")

        elif ast.tipoInstruccion == TipoInstruccion.For:    #For espera ->  var_id rango instrucciones
            variable_id = ast.hijos[0].lexema
            
            rango = ast.hijos[1]
            
            instrucciones = ast.hijos[2]

            print("For------------------\n")
            print(variable_id, " var_id")
            
            print("Rango:")
            recorrer(rango)
            
            #recorrer(instrucciones)

            print("---------------------\n")
        
        elif ast.tipoInstruccion == TipoInstruccion.DeclaracionStruct:  #Struct espera -> id campos
            id_struct = ast.hijos[0].lexema
            
            campos = ast.hijos[1]

            print("Struct---------------\n")
            print(id_struct, " id_struct")
            
            recorrer(campos)
            
            #recorrer(instrucciones)

            print("---------------------\n")

    elif isinstance(ast, NodoNoTerminal):                       #Si es un nodo no terminal
        if ast.tipoNoTerminal == TipoNoTerminal.Instrucciones:  #Instrucciones espera -> [Instrucciones...]
            for hijo in ast.hijos:
                recorrer(hijo)
        elif ast.tipoNoTerminal == TipoNoTerminal.DeclaracionParametros:    #DeclaracionParametros espera -> [Declaracion...]
            for parametro in ast.hijos:
                print("DeclaracionParametro: ")
                recorrer(parametro)

        elif ast.tipoNoTerminal == TipoNoTerminal.Parametros:   #Parametros espera -> [Parametro...]
            for hijo in ast.hijos:
                print("Parametro: ")
                recorrer(hijo)
        elif ast.tipoNoTerminal == TipoNoTerminal.CamposStruct:
            for hijo in ast.hijos:
                print("Campo: ")
                recorrer(hijo)
        elif ast.tipoNoTerminal == TipoNoTerminal.Atributo:
            for hijo in ast.hijos:
                print("Atributo: ")
                recorrer(hijo)
    elif isinstance(ast, TerminalTipoDato):
        print("Lexema:",ast.token.lexema, " Tipo:", ast.tipoDato)
    elif isinstance(ast, Terminal):
        print("Lexema:",ast.token.lexema)
    elif isinstance(ast, Token):
        print("Lexema:", ast.lexema)

def obtenerTipo(nodo: Nodo):
    if isinstance(nodo, NodoExpresion):
        if nodo.operador in TipoExpresionMatematica:
            if nodo.operador == TipoExpresionMatematica.Suma:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionMatematica.Suma)
                return tipo_resultado
            elif nodo.operador == TipoExpresionMatematica.Resta:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionMatematica.Resta)
                return tipo_resultado
            elif nodo.operador == TipoExpresionMatematica.Multiplicacion:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionMatematica.Multiplicacion)
                return tipo_resultado
            elif nodo.operador == TipoExpresionMatematica.Division:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionMatematica.Division)
                return tipo_resultado
            elif nodo.operador == TipoExpresionMatematica.Modulo:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionMatematica.Modulo)
                return tipo_resultado
            elif nodo.operador == TipoExpresionMatematica.Potencia:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionMatematica.Potencia)
                return tipo_resultado
            elif nodo.operador == TipoExpresionMatematica.MenosUnitario:
                tipo = obtenerTipo(nodo.hijos[0])
                tipo_resultado = obtenerTipoResultante(tipo, tipo, TipoExpresionMatematica.MenosUnitario)
                return tipo
            elif nodo.operador == TipoExpresionMatematica.Grupo:
                tipo = obtenerTipo(nodo.hijos[0])
                return tipo
        elif nodo.operador in TipoExpresionRelacional:
            if nodo.operador == TipoExpresionRelacional.Igualdad:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionRelacional.Igualdad)
                return tipo_resultado
            elif nodo.operador == TipoExpresionRelacional.Diferencia:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionRelacional.Diferencia)
                return tipo_resultado
            elif nodo.operador == TipoExpresionRelacional.MayorQue:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionRelacional.MayorQue)
                return tipo_resultado
            elif nodo.operador == TipoExpresionRelacional.MenorQue:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionRelacional.MenorQue)
                return tipo_resultado
            elif nodo.operador == TipoExpresionRelacional.MayorIgualQue:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionRelacional.MayorIgualQue)
                return tipo_resultado
            elif nodo.operador == TipoExpresionRelacional.MenorIgualQue:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionRelacional.MenorIgualQue)
                return tipo_resultado
        else:
            if nodo.operador == TipoExpresionLogica.And:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionLogica.And)
                return tipo_resultado
            elif nodo.operador == TipoExpresionLogica.Or:
                tipo_1 = obtenerTipo(nodo.hijos[0])
                tipo_2 = obtenerTipo(nodo.hijos[1])
                tipo_resultado = obtenerTipoResultante(tipo_1, tipo_2, TipoExpresionLogica.Or)
                return tipo_resultado
            elif nodo.operador == TipoExpresionLogica.Not:
                tipo = obtenerTipo(nodo.hijos[0])
                tipo_resultado = obtenerTipoResultante(tipo, tipo_2, TipoExpresionLogica.Not)
                return tipo_resultado
    elif isinstance(nodo, TerminalTipoDato):
        return nodo.tipoDato
    elif isinstance(nodo, NodoNoTerminal):
        if nodo.tipoNoTerminal == TipoNoTerminal.DeclaracionLista:
            return TipoDato.List

def obtenerTipoResultante(tipo1, tipo2, operacion):
    if operacion in TipoExpresionMatematica:
        if operacion == TipoExpresionMatematica.MenosUnitario:
            if (tipo1 == TipoDato.Int) or (tipo1 == TipoDato.Float):
                return tipo1
            else:
                raise AssertionError("No se puede operar MenosUnitario con los tipos ",tipo1)
        if tipo1 == tipo2:
            if tipo1 == TipoDato.Int and operacion == TipoExpresionMatematica.Division:
                return TipoDato.Float
            return tipo1
        elif (tipo1 == TipoDato.Float and tipo2 == TipoDato.Int) or (tipo1 == TipoDato.Int and tipo2 == TipoDato.Float):
            return TipoDato.Float
        elif (tipo1 == TipoDato.String and tipo2 == TipoDato.Int) or (tipo1 == TipoDato.Int and tipo2 == TipoDato.String):
            return TipoDato.String
        else:
            raise AssertionError("No se puede operar ",operacion," con los tipos ",tipo1," ",tipo2)
    elif operacion in TipoExpresionRelacional:
        if (tipo1 == TipoDato.Float and tipo2 == TipoDato.Int) or (tipo1 == TipoDato.Int and tipo2 == TipoDato.Float) or (tipo1 == tipo2):
            return TipoDato.Boolean
        else:
            raise AssertionError("No se puede operar ",operacion," con los tipos ",tipo1," ",tipo2)
        pass
    else:
        if operacion == TipoExpresionLogica.Not and tipo1 == TipoDato.Boolean:
            return TipoDato.Boolean
        elif tipo1 == TipoDato.Boolean and tipo2 == TipoDato.Boolean:
            return TipoDato.Boolean