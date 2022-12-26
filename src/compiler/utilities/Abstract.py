from enum import Enum
from abc import ABC, abstractmethod

"""
class TipoRetorno(Enum):
    Int = 0
    Float = 1
    String = 2
    Boolean = 3
    None_ = 4
    List = 5
    Struct = 6

    Return = 7
    Continue = 8
    Break = 9
"""

class Return:
    def __init__(self, valor, tipo_retorno, es_temporal, tipo_aux=''):
        self.valor = valor
        self.tipo_retorno = tipo_retorno
        self.es_temporal = es_temporal
        self.tipo_struct = tipo_aux
        self.true_et = ''
        self.false_et = ''

class Rango:
    def __init__(self, inicio, fin, error = False): #(5) , (1,10)
        self.inicio = inicio
        self.fin = fin
        self.Error = error

class Expresion(ABC):
    def __init__(self, linea, columna):
        self.linea = linea
        self.columna = columna
        self.true_et = true_et
        self.false_et = false_et
        self.tipo_struct = tipo_struct
    
    @abstractmethod
    def compilar(self, env): pass

class Instruccion(ABC):
    def __init__(self, linea, columna):
        self.linea = linea
        self.columna = columna
        
    @abstractmethod
    def compilar(self, env): pass