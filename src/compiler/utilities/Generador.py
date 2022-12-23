from .Entorno import Entorno

class Generador:

    generador = None
    heap = [0 for i in range(3010199)]
    stack = [0 for i in range(3010199)]
    dict_temp = {
        "H": 0, 
        "P": 0, 
        '': 0
    }
    
    def __init__(self):
        self.count_temp = 0
        self.count_label = 0
        self.codigo = ''
        self.funciones = ''
        self.nativas = ''
        self.en_funcion = False
        self.en_nativas = False
        self.temporales = []
        self.print_string = False
        self.print_list = False
        self.potencia = False
        self.to_upper = False
        self.to_lower = False
        self.modulo = False
    
    def limpiar(self):
        self.count_temp = 0
        self.count_label = 0
        self.codigo = ''
        self.funciones = ''
        self.nativas = ''
        self.en_funcion = False
        self.en_nativas = False
        self.temporales = []
        self.print_string = False
        self.print_list = False
        self.modulo = False
        Generador.generador = Generador()

    #Metodo creador del header del C3D
    def get_header(self):
        retorno = '/*----HEADER----*/\npackage main;\n\nimport (\n\t"fmt"\n)\n\n'               #Se agrega el header en caso que no tenga modulo
        if self.modulo:
            retorno = '/*----HEADER----*/\npackage main;\n\nimport (\n\t"fmt"\n\t"math"\n)\n\n' #Si hay modulo se usa el header importando el paquete fmt.math de Go

        if len(self.temporales) > 0:                        #Si hay variables temporales se agregan
            retorno += "var "
            for temporal in range(len(self.temporales)):
                retorno += self.temporales[temporal]
                if temporal != (len(self.temporales) - 1):  #Se toma en cuenta no agregar una trailing-comma
                    retorno += ", "
            
            retorno += " float64;\n"                        #Las temporales son definidas con el tipo float64
        
        retorno += "var P, H float64;\nvar stack [30101999]float64;\nvar heap [30101999]float64;\n\n"   #Se agregan las variables del heap y el stack a Go
        return retorno
    
    #Metodo generador del codigo C3D
        #Se agrega el header (self.get_header)
        #Se agrega el codigo declarando las funciones nativas (self.nativas)
        #Se agrega el codigo declarando las funciones no-nativas (self.funciones)
        #Se agrega el codigo restante (self.codigo)
    def get_codigo(self):
        return f'{self.get_header()}{self.nativas}\n{self.funciones}\nfunc main(){{\n{self.codigo}\n}}'
    
    #Metodo que agrega un pedazo de codigo al resto del codigo del C3D
    def code_in(self, codigo, tab="\t"):
        if self.en_nativas:                                 #Se comprueba si se quiere agregar una funcion nativa
            if self.nativas == '':                          #Si es la primera funcion nativa en el C3D se agrega el comentario indicando su inicio
                self.nativas += "/*-----NATIVAS-----*/\n"
            self.nativas += tab + codigo                    #Se agrega el codigo de la nativa

        elif self.en_funcion:                                   #Se comprueba si se quiere agregar una funcion no-nativa   
            if self.funciones == '':                            #Si es la primera funcion no-nativa en el C3D se agrega el comentario indicando su inicio
                self.funciones += "/*-----FUNCIONES-----*/\n"
            self.funciones += tab + codigo                      #Se agrega el codigo de la funcion
        
        else:                               #En caso que no sea nativa o no-nativa se agrega el codigo al codigo restante previamente creado
            self.codigo += "\t" + codigo
    
    #Metodo que agrega un comentario al codigo Go C3D
    def agregar_comentario(self, comentario):
        self.code_in(f'/* {comentario} */\n')
    
    #Metodo que retorna una instancia del Generador
    #RETORNA: Generador
    def get_instance(self):
        if Generador.generador == None:         #Si no existe una instancia se crea, caso contrario se devuelve la creada previamente
            Generador.generador = Generador()
        return Generador.generador
    
    #Metodo que agrega una nueva linea al C3D en Go
    def agregar_espacio(self):
        self.code_in("\n")
    
    #Metodo que agrega variables temporales
    #RETORNA: String con "t{numero de variable temporal creada}"
    def agregar_temporal(self):
        temporal = f't{self.count_temp}'                    #Se crea el numero de temporal de modo que quede "t{numero de temporal creada}"
        Generador.dict_temp[temporal] = 0                   #Se hace que el valor en el diccionario de temporales de la temporal creada sea igualado a 0
        self.count_temp += 1                                #Se aumenta el numero de temporales en 1
        self.temporales.append(temporal)                    #Se agrega la temporal al codigo de temporales en C3D
        return temporal                                     #Se retorna el string
    
    #Metodo que crea nuevas etiquetas
    #RETORNA: String con "L{numero de etiqueta creada}"
    def nueva_etiqueta(self):
        etiqueta = f'L{self.count_label}'   #Se crea el string de la etiqueta
        self.count_label += 1               #Se aumenta la cuenta de etiquetas en 1
        return etiqueta                     #Se retorna el string

    #Metodo que agrega etiqueta en el C3D de Go
    def poner_etiqueta(self, etiqueta):
        self.code_in(f'{etiqueta}:\n')
    
    #Metodo que agrega Goto al C3D
    def agregar_goto(self, etiqueta):
        self.code_in(f'goto {etiqueta};\n')

    #Metodo que agrega la definicion de If en C3D en Go
    #Con formato:
        #if left op right goto etiqueta
    def agregar_if(self, left, right, op, etiqueta):
        self.code_in(f'if {left} {op} {right} {{goto {etiqueta};}}\n')
    
    #Metodo que agrega expresiones en C3D en Go
    #Con formato:
        #resultado = left op right
    def agregar_expresion(self, resultado, left, right, op):

        #Se comprueba si los lados tanto izquierdo como derecho estan como temporales en el diccionario de temporales
        if left in Generador.dict_temp.keys() and right in Generador.dict_temp.keys():

            #Se guarda como valor en el diccionario de temporales en la entrada de resultado el string con la operacion realizada
            Generador.dict_temp[resultado] = self.operaciones(
                Generador.dict_temp[left], Generador.dict_temp[right], op   #Se obtiene el valor de los lados usando las entradas en el diccionario
            )

        #Se comprueba si solo el lado izquierdo es una temporal en el diccionario
        elif left in Generador.dict_temp.keys():

            #Se guarda como valor en el diccionario de temporales en la entrada de resultado el string con la operacion realizada
            Generador.dict_temp[resultado] = self.operaciones(

                #Se convierte en float el lado derecho de la operacion (el que no es un temporal en este caso), se obtiene el valor de la izquierda del diccionario
                Generador.dict_temp[left], float(right), op
            )
        
        #Se comprueba si solo el lado derecho es una temporal en el diccionario
        elif right in Generador.dict_temp.keys():

            #Se guarda como valor en el diccionario de temporales en la entrada de resultado el string con la operacion realizada
            Generador.dict_temp[resultado] = self.operaciones(

                #Se convierte en float el lado izquierdo de la operacion (el que no es un temporal en este caso), se obtiene el valor de la derecha del diccionario
                float(left), Generador.dict_temp[right], op)
        
        #Si no se cumplen los anteriores, significa que ningun lado de la operacion es temporal
        else:

            #Se guarda como valor en el diccionario de temporales en la entrada de resultado el string con la operacion realizada
            Generador.dict_temp[resultado] = self.operaciones(

                #Se convierte en float ambos lados de la operacion (ya que no son temporales)
                float(left), float(right), op)
        
        #Se agrega al codigo el C3D de la operacion
        self.code_in(f'{resultado}={left}{op}{right};\n')
    
    #Metodo que agrega modulo al C3D en Go
    #Con formato:
        #resultado = math.Mod(left, right);
    def agregar_modulo(self, resultado, left, right):
        self.modulo = True                                          #Se indica la existencia de modulo en la flag
        self.code_in(f'{resultado} = math.Mod({left},{right});\n')

    #Metodo que agrega truncate al C3D en Go
    #Con formato:
        #resultado = math.Floor(data);
    def agregar_truncate(self, resultado, data):
        self.modulo = True                                      #Se indica la existencia de modulo en la flag
        self.code_in(f'{resultado} = math.Floor({data});\n')

    #Metodo que agrega el inicio de una funcion en Go en el C3D
    #Con formato:
        #func id(){
    def agregar_inicio_funcion(self, id):
        if not self.en_nativas:                #Se comprueba si estamos en una funcion nativa
            self.en_funcion = True              #Si NO estamos en una funcion nativa se activa la flag de que estamos en una funcion no-nativa
        self.code_in(f'func {id}(){{\n', '')

    #Metodo que agrega el final de una funcion en Go en el C3D
    #Con formato:
        #return;
        #}
    def agregar_fin_funcion(self):
        self.code_in('return;\n}\n')    #Se agrega el codigo C3D
        if not self.en_nativas:        #Se comprueba si estamos en una funcion nativa
            self.in_func = False        #Si NO estamos en una funcion nativa se desactiva la flag de que estamos en una funcion no-nativa
    
    #Metodo que pone valores en posiciones del Stack
    def set_stack(self, posicion, valor):

        #Se comprueba si ambos la posicion y el valor a agregar estan en el diccionario de temporales
        if posicion in Generador.dict_temp.keys() and valor in Generador.dict_temp.keys():
            
            #Se agrega al stack en la posicion indicada el valor indicado
            Generador.stack[int(Generador.dict_temp[posicion])] = Generador.dict_temp[valor]

        #Se comprueba si solo la posicion esta en el diccionario de temporales
        elif posicion in Generador.dict_temp.keys():
            
            #Se agrega al stack en la posicion indicada el valor casteado a float
            Generador.stack[int(Generador.dict_temp[posicion])] = float(valor)

        #Se comprueba si solo el valor esta guardado en el diccionario de temporales
        elif valor in Generador.dict_temp.keys():
        
            #Se agrega al stack en la posicion el valor del diccionario
            Generador.stack[posicion] = Generador.dict_temp[valor]
        
        #En caso de que ni posicion ni valor este guardado en el stack
        else:
            
            #Se agrega en la posicion el valor al stack
            Generador.stack[posicion] = (float(valor))

        #Se agrega el codigo del manejo del stack en C3D en Go
        self.code_in(f'stack[int({posicion})]={valor};\n')

    #Metodo que pone valores del stack al diccionario de temporales
    def get_stack(self, llave, posicion):
        
        #Se comprueba si la posicion existe en el diccionario
        if posicion in Generador.dict_temp.keys():
            
            #Se guarda de la posicion indicada en el stack a la llave del diccionario el valor
            Generador.dict_temp[llave] = Generador.stack[int(Generador.dict_temp[posicion])]

        #En caso de que la posicion indicada no existe en el diccionario
        else:
            #Se guarda de la posicion en el stack a la llave del diccionario el valor
            Generador.dict_temp[llave] = Generador.stack[int(posicion)]
        
        #Se escribe la asignacion del valor del stack en C3D en Go
        self.code_in(f'{llave}=stack[int({posicion})];\n')
    
    #Metodo que crea en el C3D en Go el espacio para poder almacenar un nuevo entorno
    def nuevo_ent(self, size):
        self.code_in(f'P=P+{size};\n')

    #Metodo que llama en el C3D en Go una funcion
    def call_fun(self, id):
        self.code_in(f'{id}();\n')

    #Metodo que retira en el C3D en Go el espacio utilizado para un entorno
    def retornar_ent(self, size):
        self.code_in(f'P=P-{size};\n')
    
    #Metodo que almacena un valor en una posicion en el heap
    def set_heap(self, posicion, value):

        #Se comprueba si ambos la posicion y el valor a agregar estan en el diccionario de temporales
        if posicion in Generador.dict_temp.keys() and value in Generador.dict_temp.keys():

            #Se agrega al heap en la posicion indicada el valor indicado
            Generador.heap[int(Generador.dict_temp[posicion])] = Generador.dict_temp[value]

        #Se comprueba si solo la posicion esta en el diccionario de temporales
        elif posicion in Generador.dict_temp.keys():

            #Se agrega al heap en la posicion indicada el valor casteado a float
            Generador.heap[int(Generador.dict_temp[posicion])] = float(value)

        #Se comprueba si solo el valor esta guardado en el diccionario de temporales
        elif value in Generador.dict_temp.keys():

            #Se agrega al heap en la posicion el valor del diccionario
            Generador.heap[posicion] = Generador.dict_temp[value]

        #En caso de que ni posicion ni valor este guardado en el heap
        else:

            #Se agrega en la posicion el valor al heap
            Generador.heap[posicion] = (float(value))

        #Se agrega el codigo del manejo del heap en C3D en Go
        self.code_in(f'heap[int({posicion})]={value};\n')

    #Metodo que pone valores del heap al diccionario de temporales
    def get_heap(self, llave, posicion):

        #Se comprueba si la posicion existe en el diccionario
        if posicion in Generador.dict_temp.keys():

            #Se guarda de la posicion indicada en el heap a la llave del diccionario el valor
            Generador.dict_temp[llave] = Generador.heap[int(Generador.dict_temp[posicion])]

        #En caso de que la posicion indicada no existe en el diccionario
        else:

            #Se guarda de la posicion en el heap a la llave del diccionario el valor
            Generador.dict_temp[llave] = Generador.heap[int(posicion)]

        #Se escribe la asignacion del valor del heap en C3D en Go
        self.code_in(f'{llave}=heap[int({posicion})];\n')

    #Metodo que cambia la posicion del heap tanto en el Generador como en el C3D
    def siguiente_heap(self):
        Generador.dict_temp["H"] = Generador.dict_temp["H"]+1
        self.code_in('H=H+1;\n')

    #Metodo que agrega print al C3D en Go
    def agregar_print(self, tipo, valor):
        self.code_in(f'fmt.Printf("%{tipo}", int({valor}));\n')

    #Metodo que agrega print al C3D en Go en caso de que el valor sea un float
    def print_float(self, tipo, valor):
        self.code_in(f'fmt.Printf("%{tipo}", {valor});\n')

    #Metodo que imprime la palabra true en el C3D
    def print_true(self):
        self.agregar_print("c", 84)    #T
        self.agregar_print("c", 114)    #r
        self.agregar_print("c", 117)    #u
        self.agregar_print("c", 101)    #e

    #Metodo que imprime la palabra false en el C3D
    def print_false(self):
        self.agregar_print("c", 70)    #F
        self.agregar_print("c", 97)     #a
        self.agregar_print("c", 108)    #l
        self.agregar_print("c", 115)    #s
        self.agregar_print("c", 101)    #e
    

    #Metodo que agrega al C3D en Go la funcion nativa print_string
    def fprint_string(self):
        if(self.print_string): #Si actualmente estamos en otro print_string se retorna
            return

        #Si no estamos ya en un print_string

        self.print_string = True    #Se activa la flag que indica que estamos en un print_string
        self.en_nativas = True      #Se activa la flag que indica que estamos en una funcion nativa

        self.agregar_inicio_funcion('print_string')     #Se agrega el inicio de la funcion

        return_et = self.nueva_etiqueta()               #Se agrega la etiqueta para moverse fuera de la funcion

        compare_et = self.nueva_etiqueta()              #Se agrega la etiqueta para moverse al final de la cadena a imprimir

        temp_p = self.agregar_temporal()                 #Se agrega un temporal puntero al stack

        temp_h = self.agregar_temporal()                    #Se agrega un temporal puntero al heap

        self.agregar_expresion(temp_p, 'P', '1', '+')       #Se agrega una expresion que aumenta en uno la posicion del puntero del heap

        self.get_stack(temp_h, temp_p)                      #Se mueve el valor desde el stack al heap

        temp_c = self.agregar_temporal()                    #Se agrega un temporal de comparacion

        self.poner_etiqueta(compare_et)                     #Se pone la etiqueta de comparacion

        self.get_heap(temp_c, temp_h)                       #Se mueve el valor del heap a la temporal de comparacion

        self.agregar_if(temp_c, '-1', '==', return_et)      #Se agrega una condicion que comprueba si el valor de la temporal de comparacion es -1

        self.agregar_print('c', temp_c)                     #Se imprime como caracter el valor de la temporal de comparacion

        self.agregar_expresion(temp_h, temp_h, '1', '+')    #Se agrega una expresion que aumenta en uno la posicion del puntero del stack

        self.agregar_goto(compare_et)   #Se agrega un goto a la etiqueta de comparacion

        self.poner_etiqueta(return_et)  #Se pone la etiqueta de retorno (que nos saca de la funcion)
        self.agregar_fin_funcion()      #Se agrega el fin de la funcion    
        self.en_nativas = False         #Se desacriva la flag que indica que estamos en una funcion nativa
        
    #Metodo que agrega al C3D en Go la funcion nativa print_array
    def fprint_array(self):
    
        #Se agregan los triggers para moverse por el array
        trigger1 = False
        trigger2 = False

        self.fprint_string()

        if(self.print_array):   #Se retornasi estamos en otro print_array
            return

        #Si no estamos en un print_array


        self.print_array = True                     #Se activa la flag que indica que estamos en un print_array
        self.en_nativas = True                      #Se activa la flag que indica que estamos en una funcion nativa
        self.agregar_inicio_funcion('print_array')

        return_et = self.nueva_etiqueta()               #Se agrega etiqueta para moverse fuera de la funcion

        compare_et = self.nueva_etiqueta()              #Se agrega etiqueta de comparacion para saber cuando se acaba el array

        print_s = self.nueva_etiqueta()                 #Se crea etiqueta para controlar los string

        print_a = self.nueva_etiqueta()                 #Se crea etiqueta para controlar los array

        temp_p = self.agregar_temporal()                #Se crea temporal puntero al stack

        temp_h = self.agregar_temporal()                #Se crea temporal puntero al heap

        self.agregar_expresion(temp_p, 'P', '1', '+')   #Se aumenta la posicion del stack en 1

        self.get_stack(temp_h, temp_p)                  #Se mueve el valor apuntado del stack al heap

        contador = self.agregar_temporal()              #Se agrega un contador de array

        size = self.agregar_temporal()                  #Se agrega un size de array

        self.get_heap(size, temp_h)                     #Se mueve el valor del heap al temporal de size

        puntero_inicial = self.agregar_temporal()       #Se agrega un temporal que apunte al inicio del array

        self.agregar_expresion(temp_, temp_h, '1', '+') #Se aumenta en uno la posicion del puntero del heap

        temp_c = self.agregar_temporal()                    #Se agrega temporal de comparacion

        self.agregar_print('c', 91)                         #Se imprime [

        self.poner_etiqueta(compare_et)                     #Se pone la etiqueta de comparacion

        self.get_heap(temp_c, temp_h)                       #Se mueve el valor del heap a la temporal de comparacion

        self.agregar_expresion(puntero_inicial, temp_c, '', '') #Se mueve el valor de la temporal de comparacion al puntero de posicion en array

        #Se agrega condicion para hacer goto afuera de la funcion en caso de que el contador sea mayor o igual que el size del arreglo
        self.agregar_if(contador, size, '>=', return_et)        

        #Se recorren los elementos en heap_a del entorno actual
        for elemento in Entorno.heap_a:
            #Por cada elemento se agrega un goto condicional hacial la etiqueta de imprimir array
            self.agregar_if(elemento, puntero_inicial, '==', print_a)
            
            #Se activa el primer trigger
            trigger1 = True

        #Se recorren los elementos en heap_s del entorno actual
        for elemento in Environment.heap_s:

            #Por cada elemento se agrega un goto condicional hacial la etiqueta de imprimir string
            self.agregar_if(elemento, temp_c, '==', print_s)
            #Se activa el segundo trigger
            trigger2 = True

        self.print_float('f', temp_c)                           #Se imprime como float el valor en el temporal de comparacion
        self.agregar_print('c', 44)                             #Se imprime ,
        self.agregar_expresion(temp_h, temp_h, '1', '+')        #Se aumenta en 1 la posicion del heap
        self.agregar_expresion(contador, contador, '1', '+')    #Se aumenta el contador en 1
        self.agregar_goto(compare_et)                           #Se agrega goto a la etiqueta de comparacion

        if(trigger1):                                               #Si estamos en el trigger de imprimir array
            self.poner_etiqueta(print_a)                            #Se pone etiqueta de imprimir array

            #Se crean temporales
            temp_aux_p = self.agregar_temporal()      #Auxiliar de stack
            temp_aux_cont = self.agregar_temporal()   #Auxiliar de contador
            temp_aux_size = self.agregar_temporal()    #Auxiliar de size
            temp_aux_c = self.agregar_temporal()      #Auxiliar de comparacion
            temp_aux_pp = self.agregar_temporal()     #Segundo auxiliar de stack
            temp_aux_h = self.agregar_temporal()      #Auxiliar de heap

            self.agregar_expresion(temp_aux_p, 'P', '', '')            #Mover valor de stack a auxiliar
            self.agregar_expresion(temp_aux_cont, contador, '', '')    #Mover valor contador a auxiliar
            self.agregar_expresion(temp_aux_size, size, '', '')        #Mover valor de size a auxiliar
            self.agregar_expresion(temp_aux_c, temp_c, '', '')         #Mover valor de comparacion a auxiliar
            self.agregar_expresion(temp_aux_pp, temp_p, '', '')        #Mover valor de stack a segundo auxiliar
            self.agregar_expresion(temp_aux_h, temp_h, '', '')         #Mover valor de heap a auxiliar
            self.agregar_expresion(contador, '0', '', '')              #Hace que valor de contador sea 0
            self.set_stack(temp_p, temp_c)                          #Mover valor de temporal de comparacion al stack
            self.call_fun("print_array")                            #Se agrega llamada a print_array

            self.agregar_expresion(contador, temp_aux_cont, '1', '+')   #Se hace que contador tenga valor del auxiliar mas 1
            self.agregar_expresion(size, temp_aux_size, '', '')         #Se hace que size tenga el valor del auxiliar
            self.agregar_expresion(temp_c, temp_aux_c, '', '')          #Se hace que temporal de comparacion tenga valor del auxiliar
            self.agregar_expresion(temp_p, temp_aux_pp, '', '')         #Se hace que temporal del stack tenga el valor del segundo auxiliar
            self.agregar_expresion(temp_h, temp_aux_h, '1', '+')        #Se hace que temporal del heap tenga el valor del auxiliar mas 1

            self.agregar_goto(compare_et)   #Se agrega goto a la etiqueta de comparacion

        if(trigger2):                                                   #Si estamos en el trigger de imprimir string
            self.poner_etiqueta(print_s)                                #Se pone etiqueta de imprimir string

            #Se crean temporales (las mismas que para el trigger1)
            temp_aux_p = self.agregar_temporal()
            temp_aux_cont = self.agregar_temporal()
            temp_aux_size = self.agregar_temporal()
            temp_aux_c = self.agregar_temporal()
            temp_aux_pp = self.agregar_temporal()
            temp_aux_h = self.agregar_temporal()

            self.agregar_expresion(temp_aux_p, 'P', '', '')             #Mover valor de stack a auxiliar
            self.agregar_expresion(temp_aux_cont, contador, '', '')     #Mover valor de contador a auxiliar
            self.agregar_expresion(temp_aux_size, size, '', '')         #Mover valor de size a auxiliar
            self.agregar_expresion(temp_aux_c, temp_c, '', '')          #Mover valor de temporal de comparacion a auxiliar
            self.agregar_expresion(temp_aux_pp, temp_p, '', '')         #Mover valor de stack al segundo auxiliar
            self.agregar_expresion(temp_aux_h, temp_h, '', '')          #Mover valor del heap a auxiliar
            self.set_stack(temp_p, temp_c)                              #Se mueve el valor de temporal de comparacion al stack
            self.call_fun("print_string")                               #Se llama a funcion print_string

            self.agregar_expresion('P', temp_aux_p, '', '')             #Stack adquiere valor de auxiliar
            self.agregar_expresion(contador, temp_aux_cont, '1', '+')   #Contador adquiere valor de auxiliar
            self.agregar_expresion(size, temp_aux_size, '', '')         #Size adquiere valor de auxiliar
            self.agregar_expresion(temp_c, temp_aux_c, '', '')          #Temporal de comparacion adquiere valor del auxiliar
            self.agregar_expresion(temp_p, temp_aux_pp, '', '')         #Temporal de stack adquiere valor de segundo auxiliar
            self.agregar_expresion(temp_h, temp_aux_h, '1', '+')        #Temporal de heap adquiere valor de auxiliar 
            self.agregar_print('c', 44)                                 #Se imprime ,

            self.agregar_goto(compare_et)                               #Se agrega goto a etiqueta de comparacion

        self.poner_etiqueta(return_et)                  #Se pone etiqueta hacia fuera de la funcion
        self.agregar_print('c', 93)                     #Se imprime ]
        self.agregar_expresion(contador, '0', '', '')   #El contador se convierte en 0
        self.agregar_fin_funcion()                      #Se agrega final de funcion
        self.en_nativas = False                         #Se desactiva la flag que indica que estamos en una funcion nativa
        
    #Metodo que realiza operaciones ingresadas
    def operaciones(self, left, right, op):
        #Se intenta operar
        try:
            if(op == '+'):
                return left + right
            elif(op == '-'):
                return left - right
            elif(op == '*'):
                return left * right
            elif(op == '/'):
                return left / right
            elif(op == '%'):
                return left % right
            elif(op == '**'):
                return left ** right
            else:                       #Si no hay operador se devuelve el valor de la izquierda
                return left

        #Si hay un error se retorna
        except:
            return 

    def f_to_upper(self):
        if(self.to_upper):
            return
        self.to_upper = True
        self.en_nativas = True

        self.agregar_inicio_funcion('to_upper')         #Se agrega el inicio de la funcion

        return_et = self.nueva_etiqueta()               #Se crea etiqueta para moverse fuera de la funcion

        compare_et = self.nueva_etiqueta()              #Se crea etiqueta de comparacion para detectar fin del string

        temp_p = self.agregar_temporal()                #Se crea temporal puntero a stack

        temp_h = self.agregar_temporal()                #Se crea temporal puntero a heap

        self.agregar_expresion(temp_p, 'P', '1', '+')   #Se aumenta la posicion del stack en 1

        self.get_stack(temp_h, temp_p)                  #Se mueve el valor del stack al heap

        temp_c = self.agregar_temporal()                #Se crea temporal de comparacion

        self.poner_etiqueta(compare_et)                 #Se pone la etiqueta de comparacion

        self.get_heap(temp_c, temp_h)                   #Se mueve el valor del heap al stack

        self.agregar_if(temp_c, '-1', '==', return_et)  #Se crea goto condicional que comprueba si el temporal de comparacion tiene valor de -1

        temp = self.agregar_temporal()                  #Se agrega temporal

        pass_et = self.nueva_etiqueta()                 #Se crea etiqueta de conversion

        self.agregar_if(temp_c, '97', '<', pass_et)     #Goto condicional hacia la etiqueta de conversion para comprobar si valor es mayuscula

        self.agregar_if(temp_c, '122', '>', pass_et)    #Goto condicional hacia etiqueta de conversion para comprobar si el valor no es minuscula

        self.agregar_expresion(temp, temp_c, '32', '-') #Se reduce en 32 el valor de temporal de comparacion y se guarda en temporal (se convierte en minuscula)

        self.set_heap(temp_h, temp)                     #Se guarda el valor de temporal en el heap

        self.poner_etiqueta(pass_et)                    #Se pone la etiqueta de conversion

        self.agregar_expresion(temp_h, temp_h, '1', '+')#Se aumenta en 1 la posicion del heap

        self.agregar_goto(compare_et)       #Se agrega goto a etiqueta condicional

        self.poner_etiqueta(return_et)      #Se pone la etiqueta de salida de la funcion

        self.agregar_fin_funcion()          #Se agrega fin de funcion

        self.en_nativas = False             #Se desactiva flag que indica que se esta en una funcion nativa

    def f_to_lower(self):
        if(self.to_lower):
            return
        self.to_lower = True
        self.en_nativas = True

        self.agregar_inicio_funcion('to_lower')

        return_et = self.nueva_etiqueta()               #Se crea etiqueta para moverse fuera de la funcion

        compare_et = self.nueva_etiqueta()              #Se crea etiqueta de comparacion para detectar fin del string

        temp_p = self.agregar_temporal()                #Se crea temporal puntero a stack

        temp_h = self.agregar_temporal()                #Se crea temporal puntero a heap

        self.agregar_expresion(temp_p, 'P', '1', '+')   #Se aumenta la posicion del stack en 1

        self.get_stack(temp_h, temp_p)                  #Se mueve el valor del stack al heap

        temp_c = self.agregar_temporal()                #Se crea temporal de comparacion

        self.poner_etiqueta(compare_et)                 #Se pone la etiqueta de comparacion

        self.get_heap(temp_c, temp_h)                   #Se mueve el valor del heap al stack

        self.agregar_if(temp_c, '-1', '==', return_et)  #Se crea goto condicional que comprueba si el temporal de comparacion tiene valor de -1

        temp = self.agregar_temporal()                  #Se agrega temporal

        pass_et = self.nueva_etiqueta()                 #Se crea etiqueta de conversion

        self.agregar_if(temp_c, '65', '<', pass_et)     #Goto condicional hacia la etiqueta de conversion para comprobar si valor es minuscula

        self.agregar_if(temp_c, '90', '>', pass_et)     #Goto condicional hacia etiqueta de conversion para comprobar si el valor no es mayuscula

        self.agregar_expresion(temp, temp_c, '32', '+') #Se aumenta en 32 el valor de temporal de comparacion y se guarda en temporal (se convierte en mayuscula)

        self.set_heap(temp_h, temp)                     #Se guarda el valor de temporal en el heap

        self.poner_etiqueta(pass_et)                    #Se pone la etiqueta de conversion

        self.agregar_expresion(temp_h, temp_h, '1', '+')#Se aumenta en 1 la posicion del heap

        self.agregar_goto(compare_et)   #Se agrega goto a etiqueta condicional

        self.poner_etiqueta(return_et)  #Se pone la etiqueta de salida de la funcion

        self.agregar_fin_funcion()      #Se agrega fin de funcion

        self.en_nativas = False         #Se desactiva flag que indica que se esta en una funcion nativa

    def f_potencia(self):
        if(self.potencia):
            return

        self.potencia = True
        self.en_nativas = True
        self.agregar_inicio_funcion('potencia')
        t0 = self.agregar_temporal()

        self.agregar_expresion(t0, 'P', '1', '+')
        t1 = self.agregar_temporal()

        self.get_stack(t1, t0)
        self.agregar_expresion(t0, t0, '1', '+')
        t2 = self.agregar_temporal()

        self.get_stack(t2, t0)
        self.agregar_expresion(t0, t1, '', '')
        L0 = self.nueva_etiqueta()
        L1 = self.nueva_etiqueta()

        self.poner_etiqueta(L0)
        self.agregar_if(t2, '1', '<=', L1)
        self.agregar_expresion(t1, t1, t0, '*')
        self.agregar_expresion(t2, t2, '1', '-')
        self.agregar_goto(L0)
        self.poner_etiqueta(L1)
        self.set_stack('P', t1)
        self.agregar_fin_funcion()
        self.en_nativas = False
