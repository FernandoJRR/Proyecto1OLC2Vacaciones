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
    Incerteza="INCERTEZA"               #Se espera -> expresion INCERTEZA expresion

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
        return f"Terminal({self.token},Tipo:{self.tipoDato})"

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
