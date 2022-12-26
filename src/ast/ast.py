from enum import Enum
from ..compiler.utilities.Abstract import *
#from ..compiler.utilities.Generador import Generador

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
    Struct = 6

    Return = 7
    Continue = 8
    Break = 9

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

def recorrer(ast: Nodo, entorno): #compile == recorrer
    # Se obtiene el tipo de nodo a recorrer
    
    from ..compiler.utilities.Generador import Generador
    from ..compiler.utilities.Entorno import Entorno, Simbolo
    
    if isinstance(ast, NodoInstruccion):                        #Si es un nodo de instruccion
        if ast.tipoInstruccion == TipoInstruccion.Asignacion:   #Asignacion espera -> id tipo? valor
            
            
            #Se comprueba si el primer hijo es un token
            if isinstance(ast.hijos[0], Token):
                #Se obtiene el id al que se quiere asignar
                id_var = ast.hijos[0].lexema
                linea_var = ast.hijos[0].linea
                columna_var = ast.hijos[0].columna
            elif isinstance(ast.hijos[0], Terminal):
                #Se obtiene el id al que se quiere asignar
                id_var = ast.hijos[0].token.lexema
                linea_var = ast.hijos[0].token.linea
                columna_var = ast.hijos[0].token.columna
            else:
                id_var = ast.hijos[0]
                linea_var = 0            
                columna_var = 0            
            
            #Se verifica el tipo de dato a asignar
            if isinstance(ast.hijos[1], TipoDato):              #Se comprueba si el tipo fue indicado explicitamente
                valor_var = ast.hijos[2]
            else:                                               #Si no esta explicitamente indicado explicitamente se obtiene el tipo del valor
                valor_var = ast.hijos[1]
                
            #Se imprime la asignacion
            print("Asignacion-----------\n")
            print(id_var, "id\n")
            print(linea_var,columna_var, "posicion\n")
            #print(tipo_var, "tipo\n")
            print(valor_var, "recorrido\n")
            print("---------------------\n")
            
            generador_aux = Generador()                                                 #Se crea una instancia de Generador
            generador = generador_aux.get_instance()                                    #Se obtiene una instancia del estatico Generador
            
            generador.agregar_comentario("Compilando Valor de Variable")
            valor = recorrer(valor_var, entorno)                                        #Obtenemos el valor compilado
            generador.agregar_comentario("Fin de la Compilacion del Valor de Variable")
            
            #Se verifica el tipo de dato a asignar
            if isinstance(ast.hijos[1], TipoDato):              #Se comprueba si el tipo fue indicado explicitamente
                tipo_var = ast.hijos[1]
            else:                                               #Si no esta explicitamente indicado explicitamente se obtiene el tipo del valor
                tipo_var = valor.tipo_retorno

            #Agregamos la variable a la tabla de simbolos
            nueva_variable = entorno.guardar_var(
                id_var, tipo_var, 
                (valor.tipo_retorno == TipoDato.String or valor.tipo_retorno == TipoDato.Struct or valor.tipo_retorno == TipoDato.List), 
                valor.tipo_struct,
                linea_var,
                columna_var
            )
            
            posicion_temporal = nueva_variable.posicion     #Se obtiene la posicion en la tabla de simbolos de la variable

            if not nueva_variable.es_global:                                                        #Se comprueba si la variable actual es global
                posicion_temporal = generador.agregar_temporal()                                    #Si es global se crea una temporal
                generador.agregar_expresion(posicion_temporal, 'P', nueva_variable.posicion, "+")   #El valor guardada en el stack se guarda en la temporal
                
            if valor.tipo_retorno == TipoDato.Boolean:              #Si el valor es boolean
                etiqueta_temporal = generador.nueva_etiqueta()      #Se crea una etiqueta temporal hacia despues de la asignacion, dependiendo del boolean que sea

                generador.poner_etiqueta(valor.true_et)             #Se pone una etiqueta true dependiendo del booleano
                generador.set_stack(posicion_temporal, '1')         #Se guarda en el stack en la posicion del temporal 1, siento True
                generador.agregar_goto(etiqueta_temporal)           #Se agrega un goto hacia el final de la asignacion

                generador.poner_etiqueta(valor.false_et)            #Se pone una etiqueta false dependiendo del booleano
                generador.set_stack(posicion_temporal, '0')         #Se guarda en el stack en la posicion del temporal 0, siendo False
                generador.poner_etiqueta(etiqueta_temporal)         #Se pone la etiqueta temporal para salir de la asignacion
                
            else:                                                   #En caso que no sea boolean
                generador.set_stack(posicion_temporal, valor.valor) #Se guarda en el stack en la posicion indicada el valor
            
            #Se agrega un salto de linea en el C3D
            generador.agregar_espacio()

        elif ast.tipoInstruccion == TipoInstruccion.LlamadaFuncion: #LlamadaFunction espera -> id parametros
            id_func = ast.hijos[0].token.lexema

            parametros = ast.hijos[1]

            #Se imprime la llamada
            print("Llamada-------------\n")
            print(id_func, "id\n")
            #Se imprimen los parametros
            print(parametros.hijos[0], "parametros\n")
            #print(parametros, "parametros\n")
            print("---------------------\n")
            
            if id_func == "print" or id_func == "println":              #Se comprueba si la funcion es print o println

                generador_aux = Generador()
                generador = generador_aux.get_instance()

                for parametro in parametros.hijos:
                    valor_parametro = recorrer(parametro, entorno)
                    
                    if valor_parametro.tipo_retorno == TipoDato.Int:
                        generador.agregar_print("d", valor_parametro.valor)

                    elif valor_parametro.tipo_retorno == TipoDato.Float:
                        generador.print_float("f", valor_parametro.valor)

                    elif valor_parametro.tipo_retorno == TipoDato.Boolean:
                        etiqueta_temporal = generador.nueva_etiqueta()
                        generador.poner_etiqueta(valor_parametro.true_et)
                        generador.print_true()
                        generador.agregar_goto(etiqueta_temporal)

                        generador.poner_etiqueta(valor_parametro.false_et)
                        generador.print_false()
                        generador.poner_etiqueta(etiqueta_temporal)

                    elif valor_parametro.tipo_retorno == TipoDato.String:
                        generador.fprint_string()
                        temporal_parametro = generador.agregar_temporal()

                        generador.agregar_expresion(temporal_parametro, 'P', entorno.size, '+')
                        generador.agregar_expresion(temporal_parametro, temporal_parametro, '1', '+')
                        generador.set_stack(temporal_parametro, valor_parametro.valor)
                        generador.nuevo_ent(entorno.size)
                        generador.call_fun('print_string')

                        temporal = generador.agregar_temporal()
                        generador.get_stack(temporal, 'P')
                        generador.retornar_ent(entorno.size)

                    elif valor_parametro.tipo_retorno == TipoDato.List:
                        generador.agregar_expresion('P', 'P', entorno.size, '+')
                        generador.fprint_array()
                        generador.agregar_expresion('P', 'P', entorno.size, '-')

                        temporal_parametro = generador.agregar_temporal()
                        generador.agregar_expresion(temporal_parametro, 'P', entorno.size, '+')
                        generador.agregar_expresion(temporal_parametro, temporal_parametro, '1', '+')
                        generador.set_stack(temporal_parametro, valor_parametro.valor)
                        generador.nuevo_ent(entorno.size)
                        generador.call_fun('print_array')

                        temporal = generador.agregar_temporal()
                        generador.get_stack(temporal, 'P')
                        generador.retirar_ent(entorno.size)
                    else:
                        #TODO: Struct y manejo de errores
                        pass

                    generador.agregar_print("c", 32)
                
                if id_func == "println":
                    generador.agregar_print("c", 10)
            elif id_func == "upper":
                valor = recorrer(parametros.hijos[0], entorno)
                generador_aux = Generador()
                generador = generador_aux.get_instance()

                generador.f_to_upper()
                temporal_parametro = generador.agregar_temporal()

                generador.agregar_expresion(temporal_parametro, 'P', entorno.size, '+')
                generador.agregar_expresion(temporal_parametro, temporal_parametro, '1', '+')

                generador.set_stack(temporal_parametro, valor.valor)

                generador.nuevo_ent(entorno.size)

                generador.call_fun("to_upper")

                temporal1 = generador.agregar_temporal()
                temporal2 = generador.agregar_temporal()

                generador.agregar_expresion(temporal2, 'P', '1', '+')
                generador.get_stack(temporal1, temporal2)

                return Return(temporal1, TipoDato.String, True)
            elif id_func == "lower":
                valor = recorrer(parametros.hijos[0], entorno)

                generador_aux = Generador()
                generador = generador_aux.get_instance()

                generador.f_to_lower()
                temporal_parametro = generador.agregar_temporal()

                generador.agregar_expresion(temporal_parametro, 'P', entorno.size, '+')
                generador.agregar_expresion(temporal_parametro, temporal_parametro, '1', '+')

                generador.set_stack(temporal_parametro, valor.valor)

                generador.nuevo_ent(entorno.size)

                generador.call_fun("to_lower")

                temporal1 = generador.agregar_temporal()
                temporal2 = generador.agregar_temporal()

                generador.agregar_expresion(temporal2, 'P', '1', '+')
                generador.get_stack(temporal1, temporal2)

                return Return(temporal1, TipoDato.String, True)
            else:
                funcion = entorno.get_func(id_func)
                if funcion is not None:
                    valores_parametros = []
                    generador_aux = Generador()
                    generador = generador_aux.get_instance()
                    size = entorno.size
                    for parametro in parametros.hijos:
                        valores_parametros.append(recorrer(parametro, entorno))
                    temporal = generador.agregar_temporal()
                    generador.agregar_expresion(temporal, 'P', size+1, '+')

                    auxiliar = 0
                    for parametro in valores_parametros:
                        auxiliar = auxiliar + 1
                        generador.set_stack(temporal, parametro.valor)
                        if auxiliar != len(valores_parametros):
                            generador.agregar_expresion(temporal, temporal, '1', '+')
                    generador.nuevo_ent(size)
                    generador.call_fun(id_func)
                    generador.get_stack(temporal, 'P')
                    generador.retornar_ent(size)

                    return Return(temporal, funcion[1], True)
                #En caso que sea struct
                else:
                    pass

        elif ast.tipoInstruccion == TipoInstruccion.DeclaracionFuncion: #DeclaracionFuncion espera -> id parametros (tipo)? instrucciones
            id_declar = ast.hijos[0].lexema
            linea_declar = ast.hijos[0].linea
            columna_declar = ast.hijos[0].columna
            parametros = ast.hijos[1]            

            if len(ast.hijos) == 3:
                tipo_fun = TipoDato.None_
                instrucciones = ast.hijos[2]
            else:
                tipo_fun = ast.hijos[2]
                instrucciones = ast.hijos[3]

            #Se imprime la definicion
            print("DefinicionFuncion----\n")
            print(id_declar, "id\n")
            print(parametros, "id\n")
            print(tipo_fun, "id\n")
            print(instrucciones, "id\n")


            entorno.guardar_func(id_declar, (parametros, tipo_fun ,instrucciones))

            generador_aux = Generador()
            generador = generador_aux.get_instance()

            nuevo_entorno = Entorno(entorno)
            etiqueta_retorno = generador.nueva_etiqueta()

            nuevo_entorno.et_return = etiqueta_retorno

            nuevo_entorno.size = 1

            for parametro in parametros.hijos:
                print("DeclaracionParametro: ")
                #recorrer(parametro)
                if isinstance(parametro, TerminalTipoDato):
                    nuevo_entorno.guardar_var(parametro.token.lexema, parametro.tipoDato, 
                    (parametro.tipoDato == TipoDato.String or parametro.tipoDato == TipoDato.Struct),
                    linea=parametro.token.linea, columna=parametro.token.columna
                    )
                else:
                    nuevo_entorno.guardar_var(parametro.lexema, TipoDato.None_, False, linea=parametro.linea, columna=parametro.columna)


            generador.agregar_inicio_funcion(id_declar)

            recorrer(instrucciones, nuevo_entorno)
            
            if tipo_fun is not TipoDato.None_:
                generador.poner_etiqueta(etiqueta_retorno)

            generador.agregar_comentario("TERMINA DECLARACION")
            generador.agregar_fin_funcion()

            #Se imprimen los parametros
            #recorrer(parametros)
            #print(parametros, "parametros\n")

            print("---------------------\n")
        elif ast.tipoInstruccion == TipoInstruccion.If: #If espera -> condicion instrucciones (else | elif)?
            generador_aux = Generador()
            generador: Generador = generador_aux.get_instance()

            condicion = recorrer(ast.hijos[0], entorno)

            #print("If-------------------\n")
            #print("Condicion: ")
            #recorrer(condicion)
            #Instrucciones
            #recorrer(instrucciones)
            #print(parametros, "parametros\n")

            if condicion.tipo_retorno != TipoDato.Boolean:
                #TODO manejo de errores
                print("La condicion no es de tipo booleana")
                error = {}
                error['tipo'] = "Semantico"
                error['valor'] = "La condicion no es de tipo booleana"
                #error['posicion']=str(ast.linea)+","+str(ast.columna)
                Entorno.errores.append(error)
                return

            generador.poner_etiqueta(condicion.true_et)

            #Instrucciones
            recorrer(ast.hijos[1], entorno)

            #Se verifica si existe un else o elif en el if
            if len(ast.hijos) > 2:
                extension = ast.hijos[2]
                etiqueta_salida_if = generador.nueva_etiqueta()
                generador.agregar_goto(etiqueta_salida_if)
            
            generador.poner_etiqueta(condicion.false_et)

            if len(ast.hijos) > 2:
                #Else | Elif
                recorrer(ast.hijos[2],entorno)
                generador.poner_etiqueta(etiqueta_salida_if)

            print("---------------------\n")


        elif ast.tipoInstruccion == TipoInstruccion.Else:   #Else espera -> Token(Else) instrucciones
            recorrer(ast.hijos[1], entorno)
        elif ast.tipoInstruccion == TipoInstruccion.Elif:   #Elif espera -> condicion instrucciones (else | elif)?
            
            generador_aux = Generador()
            generador: Generador = generador_aux.get_instance()

            condicion = recorrer(ast.hijos[0], entorno)

            if condicion.tipo_retorno != TipoDato.Boolean:
                #TODO manejo de errores
                print("La condicion no es de tipo booleana")
                error = {}
                error['tipo'] = "Semantico"
                error['valor'] = "La condicion no es de tipo booleana"
                #error['posicion']=str(ast.linea)+","+str(ast.columna)
                Entorno.errores.append(error)
                return
            
            #print("Condicion: ")
            #Instrucciones
            #recorrer(instrucciones)
            #print(parametros, "parametros\n")

            generador.poner_etiqueta(condicion.true_et)

            #Instrucciones
            recorrer(ast.hijos[1], entorno)

            #Se verifica si existe un else o elif en el if
            if len(ast.hijos) > 2:
                extension = ast.hijos[2]
                etiqueta_salida_if = generador.nueva_etiqueta()
                generador.agregar_goto(etiqueta_salida_if)
            
            generador.poner_etiqueta(condicion.false_et)

            if len(ast.hijos) > 2:
                #Else | Elif
                recorrer(ast.hijos[2],entorno)
                generador.poner_etiqueta(etiqueta_salida_if)
                

        elif ast.tipoInstruccion == TipoInstruccion.While:  #While espera -> condicion instrucciones
            condicion = ast.hijos[0]
            
            instrucciones = ast.hijos[1]

            #print("While---------------\n")
            #recorrer(condicion)
            #recorrer(instrucciones)
            #print("---------------------\n")

            generador_aux = Generador()
            generador = generador_aux.get_instance()

            generador.agregar_comentario("INICIA CICLO WHILE")

            continue_lbl = generador.nueva_etiqueta()
            generador.poner_etiqueta(continue_lbl)

            condition = recorrer(condicion, entorno)

            entorno.et_break = condition.false_et
            entorno.et_continue = continue_lbl

            generador.poner_etiqueta(condition.true_et)

            #verificar si se necesita un nuevo entorno
            recorrer(instrucciones, entorno)

            generador.agregar_goto(continue_lbl)
            generador.poner_etiqueta(condition.false_et)
            generador.agregar_comentario("TERMINA CICLO WHILE")
            generador.agregar_espacio()

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
        
        elif ast.tipoInstruccion == TipoInstruccion.Return:             #Return espera -> Token(Return) expresion?
            if entorno.et_return == '':
                #TODO return fuera de una funcion
                print("Return fuera de una funcion")
                error = {}
                error['tipo'] = "Semantico"
                error['valor'] = "Return fuera de una funcion"
                #error['posicion']=str(ast.linea)+","+str(ast.columna)
                Entorno.errores.append(error)
                return

            generador_aux = Generador()
            generador = generador_aux.get_instance()

            valor = recorrer(ast.hijos[1], entorno)

            if valor.tipo_retorno == TipoDato.Boolean:
                temporal_et = generador.nueva_etiqueta()
                generador.poner_etiqueta(valor.true_et)
                generador.set_stack('P', '1')
                generador.agregar_goto(temporal_et)
                generador.poner_etiqueta(valor.false_et)
                generador.set_stack('P', '0')
                generador.poner_etiqueta(temporal_et)
            else:
                generador.set_stack('P', valor.valor)
            generador.agregar_goto(entorno.et_return)
        
        elif ast.tipoInstruccion == TipoInstruccion.Continue:
            if entorno.et_continue == '':
                #TODO continue fuera de un loop
                print("Continue fuera de un loop")
                error = {}
                error['tipo'] = "Semantico"
                error['valor'] = "Continue fuera de un loop"
                #error['posicion']=str(ast.linea)+","+str(ast.columna)
                Entorno.errores.append(error)
                return
            
            generador_aux = Generador()
            generador = generador_aux.get_instance()
            generador.agregar_goto(entorno.et_continue)
        
        elif ast.tipoInstruccion == TipoInstruccion.Break:
            if entorno.et_break == '':
                #TODO break fuera de un loop
                print("Break fuera de un loop")
                error = {}
                error['tipo'] = "Semantico"
                error['valor'] = "Break fuera de un loop"
                #error['posicion']=str(ast.linea)+","+str(ast.columna)
                Entorno.errores.append(error)
                return
            
            generador_aux = Generador()
            generador = generador_aux.get_instance()
            generador.agregar_goto(entorno.et_break)

    elif isinstance(ast, NodoNoTerminal):                       #Si es un nodo no terminal
        if ast.tipoNoTerminal == TipoNoTerminal.Instrucciones:  #Instrucciones espera -> [Instrucciones...]
            for hijo in ast.hijos:
                recorrer(hijo, entorno)
        elif ast.tipoNoTerminal == TipoNoTerminal.DeclaracionParametros:    #DeclaracionParametros espera -> [Declaracion...]
            for parametro in ast.hijos:
                print("DeclaracionParametro: ")
                #recorrer(parametro)
                if isinstance(parametro, TerminalTipoDato):
                    entorno.guardar_var(parametro.token.lexema, parametro.tipoDato, (parametro.tipoDato == TipoDato.String or parametro.tipoDato == TipoDato.Struct))
                else:
                    entorno.guardar_var(parametro.lexema, TipoDato.None_, False)

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

    elif isinstance(ast, NodoExpresion):

        generador_aux = Generador()
        generador: Generador = generador_aux.get_instance()

        if ast.operador in TipoExpresionMatematica:

            if ast.operador is not TipoExpresionMatematica.MenosUnitario and ast.operador is not TipoExpresionMatematica.Grupo:

                valor1 = recorrer(ast.hijos[0],entorno)
                valor2 = recorrer(ast.hijos[1],entorno)

                temporal = generador.agregar_temporal()

                if ast.operador == TipoExpresionMatematica.Suma:
                    operador = '+'
                elif ast.operador == TipoExpresionMatematica.Resta:
                    operador = '-'
                elif ast.operador == TipoExpresionMatematica.Multiplicacion:
                    operador = '*'
                elif ast.operador == TipoExpresionMatematica.Division:
                    operador = '/'
                elif ast.operador == TipoExpresionMatematica.Modulo:
                    operador = '%'

                if ast.operador == TipoExpresionMatematica.Potencia and valor1.tipo_retorno is not TipoDato.String:

                    generador.f_potencia()
                    temporal_parametro = generador.agregar_temporal()

                    generador.agregar_expresion(temporal_parametro, 'P', entorno.size, '+')
                    generador.agregar_expresion(temporal_parametro, temporal_parametro, '1', '+')
                    generador.set_stack(temporal_parametro, valor1.valor)
                    generador.agregar_expresion(temporal_parametro, temporal_parametro, '1', '+')
                    generador.set_stack(temporal_parametro, valor2.valor)
                    generador.nuevo_ent(entorno.size)
                    generador.call_fun('potencia')

                    temporal = generador.agregar_temporal()
                    generador.get_stack(temporal, 'P')
                    generador.retornar_ent(entorno.size)
                    salida_potencia = generador.nueva_etiqueta()

                    generador.agregar_if(valor2.valor, "0", '!=', salida_potencia)
                    generador.agregar_expresion(temporal, '1', '', '')
                    generador.poner_etiqueta(salida_potencia)

                    return Return(temporal, TipoDato.Int, True)

                else:
                    if valor1.tipo_retorno == TipoDato.Float or valor2.tipo_retorno == TipoDato.Float or ast.operador == TipoExpresionMatematica.Division:
                        etiqueta1 = generador.nueva_etiqueta()
                        etiqueta2 = generador.nueva_etiqueta()

                        if ast.operador == TipoExpresionMatematica.Division:
                            generador.agregar_if(valor2.valor, '0', '==', etiqueta1)

                            auxiliar = generador.agregar_temporal()

                            generador.agregar_expresion(auxiliar, valor2.valor, '', '')

                            generador.agregar_expresion(temporal, valor1.valor, auxiliar, operador)

                            generador.agregar_goto(etiqueta2)

                            generador.poner_etiqueta(etiqueta1)

                            #Imprimir error matematico
                            generador.agregar_print('c', 109)  
                            generador.agregar_print('c', 97) 
                            generador.agregar_print('c', 116) 
                            generador.agregar_print('c', 104) 
                            generador.agregar_print('c', 32)
                            generador.agregar_print('c', 101) 
                            generador.agregar_print('c', 114) 
                            generador.agregar_print('c', 114) 
                            generador.agregar_print('c', 111) 
                            generador.agregar_print('c', 114) 

                            generador.poner_etiqueta(etiqueta2)
                        
                        elif operador == '%':
                            generador.agregar_modulo(temporal, valor1, valor2)
                        
                        else:
                            generador.agregar_expresion(temporal, valor1.valor, valor2.valor, operador)
                        
                        return Return(temporal, TipoDato.Float, True)

                    elif valor1.tipo_retorno == TipoDato.String:
                        temporal_valor1 = generador.agregar_temporal()
                        temporal_valor2 = generador.agregar_temporal()

                        temporal_retorno = generador.agregar_temporal()
                        temporal_auxiliar = generador.agregar_temporal()

                        generador.agregar_expresion(temporal_retorno, 'H', '', '')
                        generador.agregar_expresion(temporal_valor1, valor1.valor, '', '')
                        generador.agregar_expresion(temporal_valor2, valor2.valor, '', '')
                        generador.agregar_expresion(temporal_auxiliar, valor1.valor, '', '')

                        if ast.operador == TipoExpresionMatematica.Suma and valor2.tipo_retorno == TipoDato.String:
                            etiqueta_valor1 = generador.nueva_etiqueta()
                            etiqueta_valor2 = generador.nueva_etiqueta()

                            cambiador_valor1 = generador.agregar_temporal()
                            cambiador_valor2 = generador.agregar_temporal()

                            generador.get_heap(cambiador_valor1, temporal_valor1)
                            generador.get_heap(cambiador_valor2, temporal_valor2)

                            generador.poner_etiqueta(etiqueta_valor1)
                            generador.set_heap('H', cambiador_valor1)
                            generador.siguiente_heap()

                            generador.agregar_expresion(temporal_valor1, temporal_valor1, '1', '+')
                            generador.get_heap(cambiador_valor1, temporal_valor1)
                            generador.agregar_if(cambiador_valor1, '-1', '!=', etiqueta_valor1)

                            generador.poner_etiqueta(etiqueta_valor2)
                            generador.set_heap('H', cambiador_valor2)
                            generador.siguiente_heap()

                            generador.agregar_expresion(temporal_valor2, temporal_valor2, '1', '+')
                            generador.get_heap(cambiador_valor2, temporal_valor2)
                            generador.agregar_if(cambiador_valor2, '-1', '!=', etiqueta_valor2)
                            generador.set_heap('H', '-1')
                            generador.siguiente_heap()
                        elif ast.operador == TipoExpresionMatematica.Multiplicacion and valor2.tipo_retorno == TipoDato.Int:

                            etiqueta_inicial = generador.nueva_etiqueta()
                            generador.poner_etiqueta(etiqueta_inicial)
                            generador.agregar_expresion(temporal_valor1, temporal_auxiliar, '', '')
                            contador = generador.agregar_temporal()
                            generador.agregar_expresion(contador, contador, '1', '+')

                            etiqueta_valor1 = generador.nueva_etiqueta()
                            cambiador_valor1 = generador.agregar_temporal()

                            generador.get_heap(cambiador_valor1, temporal_valor1)
                            generador.poner_etiqueta(etiqueta_valor1)
                            generador.set_heap('H', cambiador_valor1)
                            generador.siguiente_heap()
                            generador.agregar_expresion(temporal_valor1, temporal_valor1, '1', '+')

                            generador.get_heap(cambiador_valor1, temporal_valor1)
                            generador.agregar_if(cambiador_valor1, '-1', '!=', etiqueta_valor1)
                            generador.agregar_expresion(temporal_valor1, temporal_valor1, '1', '-')
                            generador.agregar_if(valor2.valor, contador, '>', etiqueta_inicial)
                            generador.set_heap('H', '-1')
                            generador.siguiente_heap()

                        else:
                            #TODO manejo de errores
                            print("No se puede operar la aritmetica")
                            error = {}
                            error['tipo'] = "Semantico"
                            error['valor'] = "No se puede operar la aritmetica"
                            #error['posicion']=str(ast.linea)+","+str(ast.columna)
                            Entorno.errores.append(error)
                            pass
                        return Return(temporal_retorno, TipoDato.String, True)
                    else:
                        if operador == '%':
                            generador.agregar_modulo(temporal, valor1.valor, valor2.valor)
                        else:
                            generador.agregar_expresion(temporal, valor1.valor, valor2.valor, operador)
                        
                        return Return(temporal, TipoDato.Int, True)

            elif ast.operador == TipoExpresionMatematica.MenosUnitario:
                valor = recorrer(ast.hijos[0],entorno)
                temporal = generador.agregar_temporal()

                if valor.tipo_retorno == TipoDato.Int or valor.tipo_retorno == TipoDato.Float:
                    generador.agregar_expresion(temporal, '0', valor.valor, '-')

                    return Return(temporal, valor.tipo_retorno, True)
                
                else:
                    #TODO manejo de error
                    print("Error en operador MenosUnitario")
                    error = {}
                    error['tipo'] = "Semantico"
                    error['valor'] = "El valor no es int o float para el operador MenosUnitario"
                    #error['posicion']=str(ast.linea)+","+str(ast.columna)
                    Entorno.errores.append(error)
                    pass

            elif ast.operador == TipoExpresionMatematica.Grupo:
                resultado = recorrer(ast.hijos[0],entorno)
                return resultado

        elif ast.operador in TipoExpresionRelacional:

            print("Compruebaaa0")
            valor1 = recorrer(ast.hijos[0], entorno)
            print("Compruebaaa1")
            #valor2 = recorrer(ast.hijos[1], entorno)
            valor2 = None

            resultado = Return(None, TipoDato.Boolean, False)

            if valor1.tipo_retorno is not TipoDato.Boolean:
                print("Compruebaaaibool")
                valor2 = recorrer(ast.hijos[1],entorno)
                print("Compruebaaaibool1.5", valor1.valor, valor2.valor)
                if (valor1.tipo_retorno == TipoDato.Int or valor1.tipo_retorno == TipoDato.Float) and (valor2.tipo_retorno == TipoDato.Int or valor2.tipo_retorno == TipoDato.Float):
                    print("Compruebaaaibool2")
                    true_et = ''
                    false_et = ''

                    if true_et == '':
                        true_et = generador.nueva_etiqueta()

                    if false_et == '':
                        false_et = generador.nueva_etiqueta()

                    if ast.operador == TipoExpresionRelacional.Igualdad:
                        operador = "=="
                    elif ast.operador == TipoExpresionRelacional.Diferencia:
                        operador = "!="
                    elif ast.operador == TipoExpresionRelacional.MayorQue:
                        operador = ">"
                    elif ast.operador == TipoExpresionRelacional.MenorQue:
                        operador = "<"
                    elif ast.operador == TipoExpresionRelacional.MayorIgualQue:
                        operador = ">="
                    elif ast.operador == TipoExpresionRelacional.MenorIgualQue:
                        operador = "<="

                    generador.agregar_if(valor1.valor, valor2.valor, operador, true_et)
                    generador.agregar_goto(false_et)
                
                elif valor1.tipo_retorno == TipoDato.String and valor2.tipo_retorno == TipoDato.String:
                    print("Compruebaaaibool3")
                    etiqueta_inicial = generador.nueva_etiqueta()

                    puntero1 = generador.agregar_temporal()
                    puntero2 = generador.agregar_temporal()

                    primer_valor = generador.agregar_temporal()
                    segundo_valor = generador.agregar_temporal()

                    true_et = ''
                    false_et = ''

                    if true_et == '':
                        true_et = generador.nueva_etiqueta()

                    if false_et == '':
                        false_et = generador.nueva_etiqueta()
                    
                    generador.agregar_expresion(puntero1, valor1.valor, '', '')
                    generador.agregar_expresion(puntero2, valor2.valor, '', '')

                    generador.poner_etiqueta(etiqueta_inicial)

                    generador.agregar_if(primer_valor, '-1', '==', true_et)

                    generador.get_heap(primer_valor, puntero1)
                    generador.get_heap(segundo_valor, puntero2)
                
                    generador.agregar_expresion(puntero1, puntero1, '1', '+')
                    generador.agregar_expresion(puntero2, puntero2, '1', '+')

                    generador.agregar_if(primer_valor, segundo_valor, '==', etiqueta_inicial)
                    generador.agregar_if(primer_valor, segundo_valor, '!=', etiqueta_inicial)
                    generador.agregar_goto(false_et)

            else:
                print("Compruebaaa")
                valor2_goto = generador.nueva_etiqueta()
                temporal_valor1 = generador.agregar_temporal()

                generador.poner_etiqueta(valor1.true_et)
                generador.agregar_expresion(temporal_valor1, '1', '', '')

                generador.agregar_goto(valor2_goto)
                generador.poner_etiqueta(valor1.false_et)

                generador.agregar_expresion(temporal_valor1, '0', '', '')
                generador.poner_etiqueta(valor2_goto)

                valor2 = recorrer(ast.hijos[1],entorno)

                if valor2.tipo_retorno != TipoDato.Boolean:
                    #TODO  manejo de errores
                    print("La variable no es de tipo booleana")
                    error = {}
                    error['tipo'] = "Semantico"
                    error['valor'] = "La variable no es de tipo booleana"
                    #error['posicion']=str(ast.linea)+","+str(ast.columna)
                    Entorno.errores.append(error)
                    return

                final_goto = generador.nueva_etiqueta()
                temporal_valor2 = generador.agregar_temporal()
                generador.poner_etiqueta(valor2.true_et)
                generador.agregar_expresion(temporal_valor2, '1', '', '')
                generador.agregar_goto(final_goto)
                generador.poner_etiqueta(valor2.false_et)
                generador.agregar_expresion(temporal_valor2, '0', '', '')
                generador.poner_etiqueta(final_goto)


                true_et = ''
                false_et = ''

                if true_et == '':
                    true_et = generador.nueva_etiqueta()

                if false_et == '':
                    false_et = generador.nueva_etiqueta()

                if ast.operador == TipoExpresionRelacional.Igualdad:
                    operador = "=="
                elif ast.operador == TipoExpresionRelacional.Diferencia:
                    operador = "!="
                elif ast.operador == TipoExpresionRelacional.MayorQue:
                    operador = ">"
                elif ast.operador == TipoExpresionRelacional.MenorQue:
                    operador = "<"
                elif ast.operador == TipoExpresionRelacional.MayorIgualQue:
                    operador = ">="
                elif ast.operador == TipoExpresionRelacional.MenorIgualQue:
                    operador = "<="

                generador.agregar_if(temporal_valor1, temporal_valor2, operador, true_et)

                generador.agregar_goto(false_et)

            generador.agregar_espacio()

            resultado.true_et = true_et
            resultado.false_et = false_et
            return resultado


        else:
            generador.agregar_comentario("inicio expresion logica")
            true_et = ''
            false_et = ''

            if true_et == '':
                true_et = generador.nueva_etiqueta()

            if false_et == '':
                false_et = generador.nueva_etiqueta()
            
            etiqueta_and_or = ''

            generador.agregar_comentario("val1")
            valor1 = recorrer(ast.hijos[0], entorno)
            generador.agregar_comentario("val1")

            if ast.operador == TipoExpresionLogica.And:
                etiqueta_and_or = valor1.true_et
            elif ast.operador == TipoExpresionLogica.Or:
                etiqueta_and_or = valor1.false_et

            if etiqueta_and_or is not '':
                generador.agregar_comentario("andor")
                generador.poner_etiqueta(etiqueta_and_or)
                generador.agregar_comentario("andor")
                pass

            if ast.operador is not TipoExpresionLogica.Not:
                generador.agregar_comentario("val2")
                valor2 = recorrer(ast.hijos[1], entorno)
                generador.agregar_comentario("val2")

            if ast.operador == TipoExpresionLogica.And:
                true_et = valor2.true_et
                false_et = valor1.false_et +":"+ valor2.false_et

            elif ast.operador == TipoExpresionLogica.Or:
                true_et = valor1.true_et + ":" + valor2.true_et
                false_et = valor2.false_et
            else:
                false_et = valor1.true_et
                true_et = valor1.false_et
            
            if valor1.tipo_retorno is not TipoDato.Boolean:
                #TODO manejo de errores
                print("La variable no es de tipo booleana")
                error = {}
                error['tipo'] = "Semantico"
                error['valor'] = "La variable no es de tipo booleana"
                #error['posicion']=str(ast.linea)+","+str(ast.columna)
                Entorno.errores.append(error)
                return
            
            if ast.operador is not TipoExpresionLogica.Not:
                if valor2.tipo_retorno is not TipoDato.Boolean:
                    return
            
            generador.agregar_espacio()

            generador.agregar_comentario("fin expresion logica")

            retorno = Return(None, TipoDato.Boolean, False)
            retorno.true_et = true_et
            retorno.false_et = false_et
            return retorno

    elif isinstance(ast, TerminalTipoDato):                         #TerminalTipoDato espera -> Token TipoDato     

        
        print(f'Lexema: -{ast.token.lexema}-',"Tipo: ", ast.tipoDato)
        
        generador_aux = Generador()                 #Se crea un Generador
        generador = generador_aux.get_instance()    #Se instancia el generador estadico
        
        #Se establece las etiquetas de boolean
        true_et = ''
        false_et = ''
        
        if ast.tipoDato == TipoDato.Int or ast.tipoDato == TipoDato.Float:      #Si el dato es Int o Float se devuelve un Return
            return Return(str(ast.token.lexema), ast.tipoDato, False)

        elif ast.tipoDato == TipoDato.Boolean:                                  #Si es un boolean se crean las etiquetas de true y false
            if true_et == '':
                true_et = generador.nueva_etiqueta()
            if false_et == '':
                false_et = generador.nueva_etiqueta()
            
            if ast.token.lexema == "True":                      #Si es True la variable
                generador.agregar_goto(true_et)                 #Se hace un goto hacia la asignacion de True
                generador.agregar_comentario("goto de True")
                generador.agregar_goto(false_et)

                booleano = True
            else:                                               #Si es False la variable
                generador.agregar_goto(false_et)                #Se hace un goto hacia la asignacion de False
                generador.agregar_comentario("goto de False")
                generador.agregar_goto(true_et)

                booleano = False
            
            retorno = Return(booleano, ast.tipoDato, False)   #Se retorna el booleano en un Return
            
            #Se establecen las etiquetas en el retorno
            retorno.true_et = true_et
            retorno.false_et = false_et

            return retorno
        
        elif ast.tipoDato == TipoDato.String:                           #Si es un string
            temporal_retorno = generador.agregar_temporal()             #Se crea una temporal que almacene el string
            generador.agregar_expresion(temporal_retorno, 'H', '', '')  #Se iguala la posicion del heap a la temporal

            #TODO revisar entre los dos
            #generador.set_heap('H', len(ast.token.lexema))              #Se establece en la posicion el size del string
            generador.set_heap('H', 0)              #Se establece en la posicion el size del string

            generador.siguiente_heap()                                  #Se mueve el heap una posicion
            
            for caracter in str(ast.token.lexema):                      #Para cada caracter en el string se guarda el ASCII en la posicion del heap
                generador.set_heap('H', ord(caracter))
                generador.siguiente_heap()

            generador.set_heap('H', '-1')                                                   #Al final de la cadena se indica guardando un -1
            generador.siguiente_heap()
            generador.agregar_expresion(temporal_retorno, temporal_retorno, '0.12837', '+') #Se suma al temporal 0.12837
            
            #Se devuelve un Return con el temporal
            return Return(temporal_retorno, ast.tipoDato, True)
        else:
            #TODO Manejo de error  
            print("Tipo de dato incorrecto")
            error = {}
            error['tipo'] = "Semantico"
            error['valor'] = "Tipo de dato incorrecto"
            #error['posicion']=str(ast.linea)+","+str(ast.columna)
            Entorno.errores.append(error)
            pass
              

    elif isinstance(ast, Terminal):                                 #Terminal espera -> Token
        print("Lexema:",ast.token.lexema)
        
        generador_aux = Generador()
        generador = generador_aux.get_instance()
        
        generador.agregar_comentario(f'Se accede a la variable {ast.token.lexema}')
        
        variable = entorno.get_var(ast.token.lexema)

        if variable is None:
            #TODO Manejo de errores
            print("Variable no declarada")
            error = {}
            error['tipo'] = "Semantico"
            error['valor'] = "Variable no declarada"
            #error['posicion']=str(ast.linea)+","+str(ast.columna)
            Entorno.errores.append(error)
            return            

        temporal = generador.agregar_temporal()

        posicion_temporal = variable.posicion

        if not variable.es_global:
            posicion_temporal = generador.agregar_temporal()
            generador.agregar_expresion(posicion_temporal, "P", variable.posicion, "+")
        
        generador.get_stack(temporal, posicion_temporal)

        if variable.tipo is not TipoDato.Boolean:
            generador.agregar_comentario("Variable accedida")
            generador.agregar_espacio()
            return Return(temporal, variable.tipo, True)

        true_et = ''
        false_et = ''

        if true_et == '':
            true_et = generador.nueva_etiqueta()
        if false_et == '':
            false_et = generador.nueva_etiqueta()
        
        generador.agregar_if(temporal, '1', '==', true_et)
        generador.agregar_goto(false_et)
        generador.agregar_comentario("Variable accedida")
        
        retorno = Return(None, TipoDato.Boolean, False)
        retorno.true_et = true_et
        retorno.false_et = false_et
        
        return retorno

    elif isinstance(ast, Token):
        print("Lexema:", ast.lexema)

        generador_aux = Generador()
        generador = generador_aux.get_instance()
        
        generador.agregar_comentario("Se accede a la variable ", ast.lexema)
        
        variable = entorno.get_var(ast.lexema)

        if variable is None:
            #TODO Manejo de errores
            print("Variable no declarada")
            error = {}
            error['tipo'] = "Semantico"
            error['valor'] = "Variable no declarada"
            #error['posicion']=str(ast.linea)+","+str(ast.columna)
            Entorno.errores.append(error)
            return
            

        temporal = generador.agregar_temporal()

        posicion_temporal = variable.posicion

        if not variable.es_global:
            posicion_temporal = generador.agregar_temporal()
            generador.agregar_expresion(posicion_temporal, "P", variable.posicion, "+")
        
        generador.get_stack(temporal, posicion_temporal)

        if variable.tipo is not TipoDato.Boolean:
            generador.agregar_comentario("Variable accedida")
            generador.agregar_espacio()
            return Return(temporal, variable.tipo, True)

        true_et = ''
        false_et = ''

        if true_et == '':
            true_et = generador.nueva_etiqueta()
        if false_et == '':
            false_et = generador.nueva_etiqueta()
        
        generador.agregar_if(temporal, '1', '==', true_et)
        generador.agregar_goto(false_et)
        generador.agregar_comentario("Variable accedida")
        
        retorno = Return(None, TipoDato.Boolean, False)
        retorno.true_et = true_et
        retorno.false_et = false_et
        
        return retorno

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
                tipo_resultado = obtenerTipoResultante(tipo, tipo, TipoExpresionLogica.Not)
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