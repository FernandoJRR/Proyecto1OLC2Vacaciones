from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from flask_codemirror import CodeMirror
from flask_codemirror.fields import CodeMirrorField
from wtforms.fields import SubmitField
import os

from src.compiler.utilities.Generador import Generador
from src.compiler.utilities.Entorno import Entorno

CODEMIRROR_LANGUAGES = ['python']
WTF_CSRF_ENABLED = True
CODEMIRROR_THEME = 'material'
SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config.from_object(__name__)


codemirror = CodeMirror(app)

class EditorForm(FlaskForm):
    source_code = CodeMirrorField(language='python', config={'lineNumbers': 'true' })
    submit = SubmitField('Submit')

@app.route("/")
def index():
    return render_template("index.html")



from src.ptp_parser import parse_input
from src.ast.ast import recorrer
@app.route("/editor", methods=['GET', 'POST'])
def editor():
    editor_area = EditorForm()
    if editor_area.validate_on_submit():
        text = editor_area.source_code.data
        
        generador_aux = Generador()
        generador_aux.limpiar()

        generador = generador_aux.get_instance()

        nuevo_entorno = Entorno(None)
        
        ast = parse_input(text)

        recorrer(ast, nuevo_entorno)

        c3d = generador.get_codigo()
        print("c3d:\n", c3d)
            
        """
        try:
        except Exception as e:
            print("Error de compilacion", e)
        """
    return render_template("editor.html", editor_area=editor_area)

