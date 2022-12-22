from ...ast.ast import *
from .Abstract import *

class Simbolo:
    
    def __init__(self, id, tipo, posicion, es_global, en_heap, struct=None, posicion_heap=False):
        self.id = id
        self.tipo = tipo
        self.posicion = posicion
        self.es_global = es_global
        self.en_heap = en_heap
        self.struct = struct
        self.posicion_heap = posicion_heap
        self.valor = None

    def __str__(self):
        return f'Id:{self.id},Tipo{self.tipo},Posicion:{self.posicion},Global:{self.es_global},Heap:{self.en_heap}'        

class Entorno:
    variables = {}
    funciones = {}
    structs = {}
    errores = []
    input_ = ""
    heap_a = []
    heap_s = []
    
    def __init__(self, entorno_anterior):
        self.variables = {}
        self.funciones = {}
        self.structs = {}
        self.entorno_anterior = entorno_anterior
        self.size = 0
        self.et_break = None
        self.et_continue = None
        self.et_return = None
        
        if entorno_anterior is not None:
            self.size = self.entorno_anterior
            self.et_break = self.entorno_anterior.et_break
            self.et_continue = self.entorno_anterior.et_continue
            self.et_return = self.entorno_anterior.et_return

    def __str__(self):
        return f'Variables:{self.variables},\nFunciones:{self.funciones},\nStructs:{self.structs}'

    #Metodo que obtiene un el contenido de un array ingresado
    #RETORNA: Array con los elementos obtenidos
    def get_items_array(self, array):
        env = self              #Se setea el entorno
        array_retorno = []      #Se crea el array a retornar
        
        #Se recorren los elementos del array
        for elemento in array:
            
            #Si el elemento es un int, boolean, str o float
            if isinstance(elemento, int) or isinstance(elemento, bool) or isinstance(elemento, str) or isinstance(elemento, float):

                #Se agrega el elemento al array
                array_retorno.append(elemento)

            #Si el elemento es un Return
            elif isinstance(elemento, Return):
                
                #Se agrega el valor del return al array
                array_retorno.append(elemento.valor)
                
            #Si el elemento es un array
            elif isinstance(elemento, list):
                
                #Se obtiene el array del array y se agrega
                array_retorno.append(self.get_items_array(elemento))
            
            #Si el elemento no coincide con ninguno de los anteriores
            else:
                valor_elemento = recorrer(elemento, env)
                #TODO: REVISAR EQUIVALENTE CON AST

                #Si el valor del elemento no es un array
                if valor_elemento.type != TipoDato.List:
                    
                    #Se agrega el valor del elemento
                    array_return.append(valor_elemento.value)

                #Si el valor del elemento es un array 
                else:
                    #Se obtiene el array del array y se agrega
                    array_return.append(self.get_items_array(valor_elemento.value))

        return array_retorno
    
    #Metodo que almacena una variable en el entorno
    #RETORNA: Simbolo de la variable
    def guardar_var(self, id_var, tipo, en_heap, tipo_struct=''):
        env = self                              #Se setea el entorno

        #Se recorren los entornos hacia el entorno padre hasta que se llega al entorno raiz
        while env is not None:

            #Se comprueba si el id existe en el entorno actual
            if id_var in env.variables.keys():

                #Si el id existe se hace que el simbolo ocupe el valor del id
                env.variables[id_var] = Simbolo(
                    id_var, tipo, env.variables[id_var].posicion,
                    env.entorno_anterior == None, en_heap, tipo_struct
                )
                
                #Se hace que las variables del entorno sean las variables del entorno actual
                Entorno.variables = env.variables
                
                #Se retorna el simbolo guardado
                return env.variables[id_var]

            #Se mueve al entorno padre
            env = env.entorno_anterior
            
        #Se comprueba si el id pertenece a una funcion
        if(id_var[-1] == '#'):
            id_var = id_var[0:-1]
            
        nuevo_simbolo = Simbolo(id_var, tipo, self.size, self.entorno_anterior == None, en_heap, tipo_struct)
        
        self.size += 1                          #Se aumenta el espacio del entorno en 1

        self.variables[id_var] = nuevo_simbolo  #Se guarda el simbolo en la llave del id

        Entorno.variables = self.variables      #Se hace que las variables del Entorno sean las variables del entorno actual
        
        return self.variables[id_var]           #Se retorna el simbolo creado

    #Metodo que almacena una funcion en el entorno
    def guardar_func(self, id_func, funcion):
        
        #Se comprueba si la funcion fue declarada anteriormente (esta repetida)
        if id_func in self.funciones.keys():
            
            #En caso de que sea el caso es un error
            #TODO Manejo de errores
            print("La funcion ya fue declarada anteriormente")
        
        #En caso que no esta repetida
        else:
            
            #Se guarda la funcion en la entrada con el id de la funcion
            self.funciones[id_func] = funcion
            
            #Se hace que las funciones del Entorno sean las funciones del entorno actual
            Environment.funciones = self.funciones

    #Metodo que almacena un struct en el entorno
    def guardar_struct(self, id_struct, campos):

        #Se comprueba si el struct fue declarado anteriormente (esta repetido)
        if id_struct in self.structs.keys():

            #En caso de que sea el caso es un error
            #TODO Manejo de errores
            print("El struct ya fue declarado anteriormente")

        #En caso que no esta repetido
        else:

            #Se guarda el struct en la entrada con el id del struct
            self.structs[id_struct] = campos

            #Se hace que los structs del Entorno sean los structs del entorno actual
            Environment.structs = self.structs

    #Metodo que retorna una variable
    #RETORNA: Simbolo con la variable si existe, None si no existe la variable
    def get_var(self, id_var):
        env = self                              #Se setea el entorno
        
        while env is not None:                  #Se recorren los entornos hacia el entorno padre en busca de la variable
            
            if id_var in env.variables.keys():  #Si la variable se encuentra en el entorno actual se devuelve
                return env.variables[id_var]
            
            env = env.entorno_anterior                      #Si la variable no se encuentra en el entorno actual se mueve al entorno padre
            
        #Si la variable no fue encontrada se devuelve None
        return None

    #Metodo que retorna una funcion
    #RETORNA: La funcion si existe, None si no existe
    def get_func(self, id_func):
        env = self                              #Se setea el entorno
        while env is not None:                  #Se recorren los entornos hacia el entorno padre en busca de la funcion

            if id_func in env.funciones.keys(): #Si la funcion se encuentra en el entorno actual se devuelve
                return env.funciones[id_func]
            
            env = env.entorno_anterior                      #Si la funcion no se encuentra en el entorno actual se mueve al entorno padre

        #Si la funcion no existe se devuelve None
        return None

    #Metodo que retorna una funcion
    #RETORNA: El struct si existe, None si no existe
    def get_struct(self, id_struct):
        env = self                              #Se setea el entorno
        
        while env is not None:                  #Se recorren los entornos hacia el entorno padre en busca del struct

            if id_struct in env.structs.keys(): #Si el struct se encuentra en el entorno actual se devuelve
                return env.structs[id_struct]

            env = env.entorno_anterior                      #Si el struct no se encuentra en el entorno actual se mueve al entorno padre
            
        #Si el struct no existe se devuelve None
        return None

    #Metodo que retorna el entorno global
    #RETORNA: Entorno global
    def get_global(self):
        env = self                      #Se setea el entorno
        
        while env.entorno_anterior is not None:     #Se mueve al entorno raiz
            env = env.entorno_anterior
        return env