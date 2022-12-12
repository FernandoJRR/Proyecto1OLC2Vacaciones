from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from flask_codemirror import CodeMirror
from flask_codemirror.fields import CodeMirrorField
from wtforms.fields import SubmitField
import os

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

@app.route("/editor", methods=['GET', 'POST'])
def editor():
    editor_area = EditorForm()
    if editor_area.validate_on_submit():
        text = editor_area.source_code.data
        parse_input(text)
    return render_template("editor.html", editor_area=editor_area)

