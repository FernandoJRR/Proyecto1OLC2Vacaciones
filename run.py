from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from flask_codemirror import CodeMirror
from flask_codemirror.fields import CodeMirrorField
from wtforms.fields import SubmitField
import os

from src.compiler.utilities.Generador import Generador
from src.compiler.utilities.Entorno import Entorno

CODEMIRROR_LANGUAGES = ['python', 'go']
WTF_CSRF_ENABLED = True
CODEMIRROR_THEME = 'material'
SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config.from_object(__name__)


codemirror = CodeMirror(app)

class EditorForm(FlaskForm):
    source_code = CodeMirrorField(id="editor_area", language='python', config={'lineNumbers': 'true' })
    submit = SubmitField('Submit')

class C3DArea(FlaskForm):
    source_code = CodeMirrorField(id="c3d_area", language='go', config={'lineNumbers': 'true', 'readOnly': 'true'})
    #source_code = CodeMirrorField(config={'lineNumbers': 'true', 'readOnly': 'true', 'mode': 'text/x-go'})
    submit = SubmitField('Submit')

class ASTArea(FlaskForm):
    source_code = CodeMirrorField(id="ast_area", config={'lineNumbers': 'false', 'readOnly': 'true'})
    #source_code = CodeMirrorField(config={'lineNumbers': 'true', 'readOnly': 'true', 'mode': 'text/x-go'})
    submit = SubmitField('Submit')
@app.route("/")
def index():
    return render_template("index.html")

from src.ptp_parser import parse_input, nivel_ast
from src.ast.ast import recorrer
@app.route("/editor", methods=['GET', 'POST'])
def editor():
    editor_area = EditorForm()
    c3d_area = C3DArea()
    ast_area = ASTArea()

    tabla_simbolos = []

    if editor_area.validate_on_submit():
        text = editor_area.source_code.data
        
        (c3d, tabla_simbolos, ast) = generar_c3d(text)

        c3d_area.source_code.data = c3d
        ast_area.source_code.data = ast
    
    return render_template("editor.html", editor_area=editor_area, c3d_area=c3d_area, ast_area=ast_area, length=len(tabla_simbolos), tabla_simbolos=tabla_simbolos)

def generar_c3d(input):
        generador_aux = Generador()
        generador_aux.limpiar()

        generador = generador_aux.get_instance()

        nuevo_entorno = Entorno(None)
        
        ast = parse_input(input)

        recorrer(ast, nuevo_entorno)

        c3d = generador.get_codigo()

        lista_variables = []
        print_var_entorno(nuevo_entorno,lista_variables)
        print("ID | Tipo | Linea | Columna")
        for var in lista_variables:
            print(f'{var[0]},{var[1]},{var[2]},{var[3]}')
        """
        try:
        except Exception as e:
            print("Error de compilacion", e)
        """
        return (c3d,lista_variables, ast)

def print_var_entorno(entorno: Entorno, lista):
    for variable in entorno.variables:
        simbolo = entorno.variables[variable]
        lista.append((variable, str(simbolo.tipo).split(".")[1], simbolo.linea, simbolo.columna))
    
    for funcion in entorno.funciones:
        lista.append((funcion, "Funcion", "-", "-"))

    for anidado in entorno.ent_anidados:
        print_var_entorno(anidado, lista)