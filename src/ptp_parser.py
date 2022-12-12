import sys
sys.path.insert(0, "../..")
from ply import *
from ply import lex
from ply import yacc
from .ast.ast import *

##### Lexer ######
#import lex
import decimal

sys.set_int_max_str_digits(50000)

tokens = (
    'DEF',
    'IF',
    'ELIF',
    'ELSE',
    'NAME',
    'NUMBER',  # Python decimals
    'FLOAT',
    'STRING',  # single quoted strings only; syntax of raw strings
    'LIST',
    'LPAR',
    'RPAR',
    'LBRA',
    'RBRA',
    'COLON',
    'EQ',
    'NEQ',
    'ASSIGN',
    'STRUCT',
    'LT',
    'GT',
    'LEQ',
    'GEQ',
    'NOT',
    'OR',
    'AND',
    'POTENCIA',
    'PLUS',
    'MINUS',
    'MULT',
    'DIV',
    'MOD',
    'RETURN',
    'CONTINUE',
    'BREAK',
    'WS',
    'NEWLINE',
    'COMMA',
    'SEMICOLON',
    'INT',
    'STR',
    'BOOL',
    'INDENT',
    'DEDENT',
    'ENDMARKER',
)

#t_NUMBER = r'\d+'
# taken from decmial.py but without the leading sign

def t_STRING(t):
    r"\"([^\\']+|\\'|\\\\)*\""  # I think this is right ...

#    ('([^\\']+|\\'|\\\\)*') |
    t.value = t.value[1:-1].encode().decode("unicode_escape")  # .swapcase() # for fun
    return t


def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = decimal.Decimal(t.value)
    if t.value == int(t.value):
        t.value = int(t.value)
    else:
        t.value = float(t.value)
    print(t,"\n")
    return t
    
def t_NUMBER(t):
    r'\d+'
    t.value = decimal.Decimal(t.value)
    if t.value == int(t.value):
        t.value = int(t.value)
    else:
        t.value = float(t.value)
    print(t,"\n")
    return t


t_COLON = r':'
t_LEQ = r'<='
t_GEQ = r'>='
t_NEQ = r'!='
t_EQ = r'=='
t_ASSIGN = r'='
t_LT = r'<'
t_GT = r'>'
t_PLUS = r'\+'
t_MINUS = r'-'
t_POTENCIA = r'\*\*'
t_MULT = r'\*'
t_DIV = r'/'
t_MOD = r'\%'
t_COMMA = r','
t_SEMICOLON = r';'

# Ply nicely documented how to do this.

RESERVED = {
    "def": "DEF",
    "if": "IF",
    "elif": "ELIF",
    "else": "ELSE",
    "return": "RETURN",
    "continue": "CONTINUE",
    "break": "BREAK",

    "struct": "STRUCT",

    "and": "AND",
    "or": "OR",
    "not": "NOT",

    "int": "INT",
    "float": "FLOAT",
    "str": "STR",
    "bool": "BOOL",
    "list": "LIST",
}


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = RESERVED.get(t.value, "NAME")
    return t

# Putting this before t_WS let it consume lines with only comments in
# them so the latter code never sees the WS part.  Not consuming the
# newline.  Needed for "if 1: #comment"


def t_comment(t):
    r"[ ]*\043[^\n]*"  # \043 is '#'
    pass


# Whitespace
def t_WS(t):
    r'[ ]+'
    if t.lexer.at_line_start and t.lexer.paren_count == 0:
        return t

# Don't generate newline tokens when inside of parenthesis, eg
#   a = (1,
#        2, 3)


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = "NEWLINE"
    if t.lexer.paren_count == 0:
        return t


def t_LPAR(t):
    r'\('
    t.lexer.paren_count += 1
    return t


def t_RPAR(t):
    r'\)'
    t.lexer.paren_count -= 1
    return t

def t_LBRA(t):
    r'\['
    #t.lexer.bra_count += 1
    return t


def t_RBRA(t):
    r'\]'
    #t.lexer.bra_count -= 1
    return t

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))
    print("Skipping", repr(t.value[0]))
    t.lexer.skip(1)

# I implemented INDENT / DEDENT generation as a post-processing filter

# The original lex token stream contains WS and NEWLINE characters.
# WS will only occur before any other tokens on a line.

# I have three filters.  One tags tokens by adding two attributes.
# "must_indent" is True if the token must be indented from the
# previous code.  The other is "at_line_start" which is True for WS
# and the first non-WS/non-NEWLINE on a line.  It flags the check so
# see if the new line has changed indication level.

# Python's syntax has three INDENT states
#  0) no colon hence no need to indent
#  1) "if 1: go()" - simple statements have a COLON but no need for an indent
#  2) "if 1:\n  go()" - complex statements have a COLON NEWLINE and must indent
NO_INDENT = 0
MAY_INDENT = 1
MUST_INDENT = 2

# only care about whitespace at the start of a line


def track_tokens_filter(lexer, tokens):
    lexer.at_line_start = at_line_start = True
    indent = NO_INDENT
    saw_colon = False
    for token in tokens:
        token.at_line_start = at_line_start

        if token.type == "COLON":
            at_line_start = False
            indent = MAY_INDENT
            token.must_indent = False

        elif token.type == "NEWLINE":
            at_line_start = True
            if indent == MAY_INDENT:
                indent = MUST_INDENT
            token.must_indent = False

        elif token.type == "WS":
            assert token.at_line_start == True
            at_line_start = True
            token.must_indent = False

        else:
            # A real token; only indent after COLON NEWLINE
            if indent == MUST_INDENT:
                token.must_indent = True
            else:
                token.must_indent = False
            at_line_start = False
            indent = NO_INDENT

        yield token
        lexer.at_line_start = at_line_start


def _new_token(type, lineno):
    tok = lex.LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    tok.lexpos = 0
    return tok

# Synthesize a DEDENT tag


def DEDENT(lineno):
    return _new_token("DEDENT", lineno)

# Synthesize an INDENT tag


def INDENT(lineno):
    return _new_token("INDENT", lineno)


# Track the indentation level and emit the right INDENT / DEDENT events.
def indentation_filter(tokens):
    # A stack of indentation levels; will never pop item 0
    levels = [0]
    token = None
    depth = 0
    prev_was_ws = False
    for token in tokens:
        # if 1:
        # print "Process", token,
        # if token.at_line_start:
        # print "at_line_start",
        # if token.must_indent:
        # print "must_indent",
        # print

        # WS only occurs at the start of the line
        # There may be WS followed by NEWLINE so
        # only track the depth here.  Don't indent/dedent
        # until there's something real.
        if token.type == "WS":
            assert depth == 0
            depth = len(token.value)
            prev_was_ws = True
            # WS tokens are never passed to the parser
            continue

        if token.type == "NEWLINE":
            depth = 0
            if prev_was_ws or token.at_line_start:
                # ignore blank lines
                continue
            # pass the other cases on through
            yield token
            continue

        # then it must be a real token (not WS, not NEWLINE)
        # which can affect the indentation level

        prev_was_ws = False
        if token.must_indent:
            # The current depth must be larger than the previous level
            if not (depth > levels[-1]):
                raise IndentationError("expected an indented block")

            levels.append(depth)
            yield INDENT(token.lineno)

        elif token.at_line_start:
            # Must be on the same level or one of the previous levels
            if depth == levels[-1]:
                # At the same level
                pass
            elif depth > levels[-1]:
                raise IndentationError(
                    "indentation increase but not in new block")
            else:
                # Back up; but only if it matches a previous level
                try:
                    i = levels.index(depth)
                except ValueError:
                    raise IndentationError("inconsistent indentation")
                for _ in range(i + 1, len(levels)):
                    yield DEDENT(token.lineno)
                    levels.pop()

        yield token

    ### Finished processing ###

    # Must dedent any remaining levels
    if len(levels) > 1:
        assert token is not None
        for _ in range(1, len(levels)):
            yield DEDENT(token.lineno)


# The top-level filter adds an ENDMARKER, if requested.
# Python's grammar uses it.
def filter(lexer, add_endmarker=True):
    token = None
    tokens = iter(lexer.token, None)
    tokens = track_tokens_filter(lexer, tokens)
    for token in indentation_filter(tokens):
        yield token

    if add_endmarker:
        lineno = 1
        if token is not None:
            lineno = token.lineno
        yield _new_token("ENDMARKER", lineno)

# Combine Ply and my filters into a new lexer


class IndentLexer(object):

    def __init__(self, debug=0, reflags=0):
        self.lexer = lex.lex(debug=debug, reflags=reflags)
        self.token_stream = None

    def input(self, s, add_endmarker=True):
        self.lexer.paren_count = 0
        self.lexer.input(s)
        self.token_stream = filter(self.lexer, add_endmarker)

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None

##########   Parser (tokens -> AST) ######

# also part of Ply
#import yacc

# I use the Python AST
import ast

# Helper function


def Assign(left, right):
    names = []
    if isinstance(left, ast.Name):
        # Single assignment on left
        return ast.Assign([ast.Name(left.id, ctx=ast.Store())], right)
    elif isinstance(left, ast.Tuple):
        # List of things - make sure they are Name nodes
        names = []
        for child in left.elts:
            if not isinstance(child, ast.Name):
                raise SyntaxError("that assignment not supported")
            names.append(child.id)
        ass_list = [ast.Name(name, ctx=ast.Store()) for name in names]
        return ast.Assign([ast.Tuple(ass_list, ctx=ast.Store())], right)
    else:
        raise SyntaxError("Can't do that yet")


# The grammar comments come from Python's Grammar/Grammar file

# NB: compound_stmt in single_input is followed by extra NEWLINE!
# file_input: (NEWLINE | stmt)* ENDMARKER
def p_file_input_end(p):
    """file_input_end : file_input ENDMARKER"""

    print(p[1],"\n")
    p[0] = p[1]


def p_file_input(p):
    """file_input : file_input NEWLINE
                  | file_input stmt
                  | NEWLINE
                  | stmt"""

    print(p[1],"\n")
    

    if isinstance(p[len(p) - 1], str):
        if len(p) == 3:
            print("1","\n")
            p[0] = p[1]
        else:
            print("2","\n")
            p[0] = []  # p == 2 --> only a blank line
    else:
        if len(p) == 3:
            p[1].agregarhijo(p[2])
            #p[0] = p[1] + p[2]
            p[0] = p[1]
        else:
            instrucciones = NodoNoTerminal(TipoNoTerminal.Instrucciones)
            instrucciones.agregarhijo(p[1])
            #p[0] = p[1]
            p[0] = instrucciones


# funcdef: [decorators] 'def' NAME parameters ':' suite
# ignoring decorators
def p_funcdef(p):
    "funcdef : DEF NAME parameters COLON suite"
    #p[0] = ast.FunctionDef(p[2], args=ast.arguments([ast.arg(x, None) for x in p[3]], None, [], [], None, []), body=p[5], decorator_list=[], returns=None)
    func_def = NodoInstruccion(TipoInstruccion.DeclaracionFuncion)
    token_id = Token(p[2], p.lineno(2), p.lexspan(2)[0])
    func_def.agregarhijos([token_id,p[3],p[5]])    
    p[0] = func_def

# parameters: '(' [varargslist] ')'


def p_parameters(p):
    """parameters : LPAR RPAR
                  | LPAR varargslist RPAR"""
    if len(p) == 3:
        p[0] = NodoNoTerminal(TipoNoTerminal.DeclaracionParametros)
    else:
        p[0] = p[2]


# varargslist: (fpdef ['=' test] ',')* ('*' NAME [',' '**' NAME] | '**' NAME) |
# highly simplified
def p_varargslist(p):
    """varargslist : varargslist COMMA NAME COLON type
                   | varargslist COMMA NAME
                   | NAME COLON type
                   | NAME
    """
    
    if len(p) == 6:
        token_id = Token(p[3], p.lineno(3), p.lexspan(3)[0])
        terminal = TerminalTipoDato(token_id, p[5])
        p[1].agregarhijo(terminal)
        p[0] = p[1]
    elif len(p) == 4:
        if isinstance(p[1], str):
            token_id = Token(p[2], p.lineno(2), p.lexspan(2)[0])
            terminal = TerminalTipoDato(token_id, p[3])
            parametros = NodoNoTerminal(TipoNoTerminal.DeclaracionParametros)
            parametros.agregarhijo(terminal)
            p[0] = parametros
        else:
            token_id = Token(p[3], p.lineno(3), p.lexspan(3)[0])
            p[1].agregarhijo(token_id)
            p[0] = p[1]
    else:
        token_id = Token(p[1], p.lineno(1), p.lexspan(1)[0])
        parametros = NodoNoTerminal(TipoNoTerminal.DeclaracionParametros)
        parametros.agregarhijo(token_id)
        p[0] = parametros

# stmt: simple_stmt | compound_stmt

types = {
    "int": TipoDato.Int,
    "float": TipoDato.Float,
    "bool": TipoDato.Boolean,
    "str": TipoDato.String,
    "list": TipoDato.List
}

def p_type(p):
    """type : STR
            | INT
            | FLOAT
            | BOOL
            | LIST
            | NAME
    """
    
    if p[1] in types:
        p[0] = types[p[1]]
    else:
        p[0] = Token(p[1], p.lineno(1), p.lexspan(1)[0])

def p_stmt_simple(p):
    """stmt : simple_stmt"""
    # simple_stmt is a list
    print(p[1],"\n")
    p[0] = p[1]


def p_stmt_compound(p):
    """stmt : compound_stmt"""
    p[0] = p[1]

# simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE


def p_simple_stmt(p):
    """simple_stmt : small_stmts NEWLINE
                   | small_stmts SEMICOLON NEWLINE"""

    print(p[1],"\nsimple_stmt")
    p[0] = p[1]


def p_small_stmts(p):
    """small_stmts : small_stmts SEMICOLON small_stmt
                   | small_stmt"""

                   
    print(p[1],"\nsmall_stmts")
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        #p[0] = [p[1]]
        p[0] = p[1]

# small_stmt: expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
#    import_stmt | global_stmt | exec_stmt | assert_stmt


def p_small_stmt(p):
    """small_stmt : flow_stmt
                  | expr_stmt"""

    print(p[1],"\nexpr_stmt")
    p[0] = p[1]

# expr_stmt: testlist (augassign (yield_expr|testlist) |
#                      ('=' (yield_expr|testlist))*)
# augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
#             '<<=' | '>>=' | '**=' | '//=')


def p_expr_stmt(p):
    """expr_stmt : testlist ASSIGN testlist
                 | testlist COLON type ASSIGN testlist
                 | testlist """
                 
    print(p[1],"\n")
                 
    if len(p) == 2:
        # a list of expressions
        #p[0] = ast.Expr(p[1])
        #p[0] = NodoExpresion(TipoExpresionMatematica.Grupo, [p[1]])
        p[0] = p[1]
    else:
        if len(p) == 4:
            asignacion = NodoInstruccion(TipoInstruccion.Asignacion)
            asignacion.agregarhijos([p[1],p[3]])
            p[0] = asignacion
            #p[0] = Assign(p[1], p[3])
        else:
            asignacion = NodoInstruccion(TipoInstruccion.Asignacion)
            asignacion.agregarhijos([p[1],p[3],p[5]])
            p[0] = asignacion
            #p[0] = Assign(p[1], p[3])



def p_flow_stmt(p):
    """flow_stmt : return_stmt
                 | continue_stmt
                 | break_stmt
    """
    p[0] = p[1]

# return_stmt: 'return' [testlist]


def p_return_stmt(p):
    """return_stmt : RETURN testlist
                   | RETURN
    """
    #p[0] = ast.Return(p[2])
    retorno = NodoInstruccion(TipoInstruccion.Return)
    token = Token(p[1], p.lineno(1), p.lexspan(1)[0])
    retorno.agregarhijo(token)
    if len(p) == 3:
        retorno.agregarhijo(p[2])
    p[0] = retorno

def p_continue_stmt(p):
    """continue_stmt : CONTINUE
    """
    continuar = NodoInstruccion(TipoInstruccion.Continue)
    token = Token(p[1], p.lineno(1), p.lexspan(1)[0])
    continuar.agregarhijo(token)
    p[0] = continuar
    

def p_break_stmt(p):
    """break_stmt : BREAK
    """
    break_ = NodoInstruccion(TipoInstruccion.Break)
    token = Token(p[1], p.lineno(1), p.lexspan(1)[0])
    break_.agregarhijo(token)
    p[0] = break_

def p_compound_stmt(p):
    """compound_stmt : if_stmt
                     | funcdef
                     | struct_def"""
    p[0] = p[1]

def p_struct_def(p):
    """struct_def : STRUCT NAME COLON struct_body
    """
    
    struct_def = NodoNoTerminal(TipoInstruccion.DeclaracionStruct)
    struct_def.agregarhijos(p[4])
    p[0] = struct_def
    
def p_struct_body(p):
    """struct_body : NEWLINE INDENT struct_fields DEDENT
    """
    p[0] = p[3]

def p_struct_fields(p):
    """struct_fields : struct_field struct_fields
                     | struct_field 
    """
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

def p_struct_field(p):
    """struct_field : NAME COLON type NEWLINE
                    | NAME NEWLINE
    """

    if len(p) == 5:
        p[0] = TerminalTipoDato(Token(p[1], p.lineno(1), p.lexspan(1)[0]), p[3])
    else:
        p[0] = Token(p[1], p.lineno(1), p.lexspan(1)[0])


def p_if_stmt(p):
    """if_stmt : IF test COLON suite
               | IF test COLON suite ELSE COLON suite
               | IF test COLON suite else_if_list
    """
    
    #p[0] = ast.If(p[2], p[4], [])
    if_instruccion = NodoInstruccion(TipoInstruccion.If)
    if_instruccion.agregarhijos([p[2],p[4]])
    #No Else
    if len(p) == 5:
        p[0] = if_instruccion

    #Else
    elif len(p) == 8:
        else_instruccion = NodoInstruccion(TipoInstruccion.Else)
        token_else = Token(p[5], p.lineno(5), p.lexspan(5)[0])
        else_instruccion.agregarhijos([token_else, p[7]])
        if_instruccion.agregarhijo(else_instruccion)
        p[0] = if_instruccion
    #Elif
    else:
        if_instruccion.agregarhijo(p[5])
        p[0] = if_instruccion


def p_else_if_list(p):
    """else_if_list     : ELIF test COLON suite
                        | ELIF test COLON suite ELSE COLON suite
                        | ELIF test COLON suite else_if_list"""

    elif_instruccion = NodoInstruccion(TipoInstruccion.Elif)
    elif_instruccion.agregarhijos([p[2],p[4]])

    #No Else
    if len(p) == 5:
        p[0] = elif_instruccion
    #Else
    elif len(p) == 8:
        else_instruccion = NodoInstruccion(TipoInstruccion.Else)
        token_else = Token(p[5], p.lineno(5), p.lexspan(5)[0])
        else_instruccion.agregarhijos([token_else, p[7]])
        elif_instruccion.agregarhijo(else_instruccion)
        p[0] = elif_instruccion
    #Elif
    else:
        elif_instruccion.agregarhijo(p[5])
        p[0] = elif_instruccion

def p_suite(p):
    """suite : simple_stmt
             | NEWLINE INDENT stmts DEDENT"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[3]


def p_stmts(p):
    """stmts : stmts stmt
             | stmt"""
    if len(p) == 3:
        #p[0] = p[1] + p[2]
        p[1].agregarhijo(p[2])
        p[0] = p[1]
    else:
        #p[0] = p[1]
        instrucciones = NodoNoTerminal(TipoNoTerminal.Instrucciones)
        instrucciones.agregarhijo(p[1])
        p[0] = instrucciones
        

# No using Python's approach because Ply supports precedence

# comparison: expr (comp_op expr)*
# arith_expr: term (('+'|'-') term)*
# term: factor (('*'|'/'|'%'|'//') factor)*
# factor: ('+'|'-'|'~') factor | power
# comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'


binary_ops = {
    "+": TipoExpresionMatematica.Suma,
    "-": TipoExpresionMatematica.Resta,
    "*": TipoExpresionMatematica.Multiplicacion,
    "/": TipoExpresionMatematica.Division,
    "%": TipoExpresionMatematica.Modulo,
    "**": TipoExpresionMatematica.Potencia
}

compare_ops = {
    "<": TipoExpresionRelacional.MenorQue,
    ">": TipoExpresionRelacional.MayorQue,
    "==": TipoExpresionRelacional.Igualdad,
    "<=": TipoExpresionRelacional.MenorIgualQue,
    ">=": TipoExpresionRelacional.MayorIgualQue,
    "!=": TipoExpresionRelacional.Diferencia
}

logical_ops = {
    "and": TipoExpresionLogica.And,
    "or": TipoExpresionLogica.Or
}

unary_ops = {
    "not": TipoExpresionLogica.Not,
    "-": TipoExpresionMatematica.MenosUnitario
}

#precedence = (
#    ("left", "EQ", "GT", "LT"),
#    ("left", "PLUS", "MINUS"),
#    ("left", "MULT", "DIV"),
#)

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'NOT'),
    ('left', 'GT', 'LT', 'GEQ', 'LEQ'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULT', 'DIV', 'MOD'),
    ('left', 'UMENOS'),
    ('right', 'POTENCIA'),
    ('nonassoc', 'GRUPO'),
)

def p_comparison(p):
    """comparison : comparison PLUS comparison
                  | comparison MINUS comparison
                  | comparison MULT comparison
                  | comparison DIV comparison
                  | comparison MOD comparison
                  | comparison POTENCIA comparison
                  | MINUS comparison %prec UMENOS
                  | comparison NEQ comparison
                  | comparison EQ comparison
                  | comparison LT comparison
                  | comparison GT comparison
                  | comparison LEQ comparison
                  | comparison GEQ comparison
                  | comparison AND comparison
                  | comparison OR comparison
                  | NOT comparison
                  | LPAR comparison RPAR %prec GRUPO
                  | power"""
    
    if len(p) == 4:
        if p[2] in binary_ops:
            p[0] = NodoExpresion(binary_ops[p[2]], [p[1],p[3]])
        elif p[2] in compare_ops:
            p[0] = NodoExpresion(compare_ops[p[2]], [p[1],p[3]])
        elif p[2] in logical_ops:
            p[0] = NodoExpresion(logical_ops[p[2]], [p[1],p[3]])
        else:
            p[0] = NodoExpresion(TipoExpresionMatematica.Grupo, [p[2]])
    elif len(p) == 3:
        p[0] = NodoExpresion(unary_ops[p[1]], [p[2]])
    else:
        p[0] = p[1]

# power: atom trailer* ['**' factor]
# trailers enables function calls.  I only allow one level of calls
# so this is 'trailer'


def p_power(p):
    """power : atom
             | atom trailer
             | atom list"""
             
    if len(p) == 2:
        p[0] = p[1]
    else:
        if p[2][0] == "LLAMADA":
            parametros = NodoNoTerminal(TipoNoTerminal.Parametros)
            parametros.agregarhijos(p[2][1])
            llamada = NodoInstruccion(TipoInstruccion.LlamadaFuncion)
            llamada.agregarhijo(p[1])
            llamada.agregarhijo(parametros)
            p[0] = llamada
        elif p[2][0] == "INDICE":
            indice = NodoNoTerminal(TipoNoTerminal.IndiceLista)
            indice.agregarhijos(p[2][1])
            p[0] = indice
        else:
            raise AssertionError("not implemented")


def p_atom_name(p):
    """atom : NAME"""
    token = Token(p[1], p.lineno(1), p.lexspan(1)[0])
    p[0] = Terminal(token)


def p_atom_number(p):
    """atom : NUMBER"""
    token = Token(p[1], p.lineno(1), p.lexspan(1)[0])
    p[0] = TerminalTipoDato(token, TipoDato.Int)

def p_atom_float(p):
    """atom : FLOAT"""
    token = Token(p[1], p.lineno(1), p.lexspan(1)[0])
    p[0] = TerminalTipoDato(token, TipoDato.Float)
    

def p_atom_string(p):
    """atom : STRING"""
    token = Token(p[1], p.lineno(1), p.lexspan(1)[0])
    p[0] = TerminalTipoDato(token, TipoDato.String)

# def p_atom_tuple(p):
#     """atom : LPAR testlist RPAR"""
#     p[0] = p[2]

# trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME


def p_trailer(p):
    "trailer : LPAR arglist RPAR"
    p[0] = ("LLAMADA", p[2])

def p_list(p):
    """list : LBRA test RBRA
            | list LBRA test RBRA
    """
    if len(p) == 4:
        p[0] = ("INDICE", [p[2]])
    else:
        p[1][1].append(p[3])
        p[0] = p[1]

# testlist: test (',' test)* [',']
# Contains shift/reduce error


def p_testlist(p):
    """testlist : testlist_multi COMMA
                | testlist_multi """
                
    
    if len(p) == 2:
        p[0] = p[1]
    else:
        # May need to promote singleton to tuple
        if isinstance(p[1], list):
            p[0] = p[1]
        else:
            p[0] = [p[1]]
    # Convert into a tuple?
    if isinstance(p[0], list):
        p[0] = ast.Tuple(p[0], ctx=ast.Load())


def p_testlist_multi(p):
    """testlist_multi : testlist_multi COMMA test
                      | test"""
 
    print(p[1],"\n")

    if len(p) == 2:
        # singleton
        p[0] = p[1]
    else:
        if isinstance(p[1], list):
            p[0] = p[1] + [p[3]]
        else:
            # singleton -> tuple
            p[0] = [p[1], p[3]]


# test: or_test ['if' or_test 'else' test] | lambdef
#  as I don't support 'and', 'or', and 'not' this works down to 'comparison'
def p_test(p):
    "test : comparison"
    p[0] = p[1]


# arglist: (argument ',')* (argument [',']| '*' test [',' '**' test] | '**' test)
# XXX INCOMPLETE: this doesn't allow the trailing comma
def p_arglist(p):
    """arglist : arglist COMMA argument
               | argument"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

# argument: test [gen_for] | test '=' test  # Really [keyword '='] test


def p_argument(p):
    "argument : test"
    p[0] = p[1]


def p_error(p):
    # print "Error!", repr(p)
    raise SyntaxError(p)


class PyToPyParser(object):

    def __init__(self, lexer=None):
        if lexer is None:
            lexer = IndentLexer()
        self.lexer = lexer
        self.parser = yacc.yacc()

    def parse(self, code):
        self.lexer.input(code)
        result = self.parser.parse(lexer=self.lexer, tracking=True)
        return result
        return ast.Module(result)

def parse_input(input):
    input = "\n".join(input.splitlines())+"\n"
    parser = PyToPyParser()
    print("input\n",input)
    ast = parser.parse(input)
    print(ast,"\n")
    print("Done")