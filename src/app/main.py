import os
import helpers

from bokeh.io import curdoc
from bokeh.events import ButtonClick
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Div, Slider, TextInput
from bokeh.models.widgets import Button

from jinja2 import Environment, FileSystemLoader

# Variables globales
method = None

# Modelos de bokeh
welcome = Div(text='Bienvenido a la TetoPolla de la Copa América 2024. Escoge una opción de abajo')

button_signin = Button(label='Iniciar sesión', button_type='primary', align='end', name='login')
button_signup = Button(label='Crear cuenta'  , button_type='primary', align='end', name='login')

username = TextInput(title='Nombre de usuario', name='username', visible=False)
password = TextInput(title='Contraseña', name='password', visible=False)

button_matches = Button(label='Partidos', button_type='primary', align='end')
button_cards   = Button(label='Mis tarjetas', button_type='primary', align='end')

button_accept = Button(label='Aceptar', button_type='success', align='end', visible=False)
button_cancel = Button(label='Cancelar', button_type='danger', align='end', visible=False)

# Callbacks
def signin():
    global method
    
    button_signin.update(visible=False)
    button_signup.update(visible=False)
    username.update(visible=True)
    password.update(visible=True)
    button_accept.update(visible=True)
    button_cancel.update(visible=True)

    method = 'signin'

def signup():
    global method

    button_signin.update(visible=False)
    button_signup.update(visible=False)
    username.update(visible=True)
    button_accept.update(visible=True)
    button_cancel.update(visible=True)

    method = 'signup'

def accept():
    global method

    status = False
    if method == 'signin':
        status = helpers.signin(username.value, password.value)
    elif method == 'signup':
        status = helpers.signup(username.value)


# Eventos
button_signin.on_event(ButtonClick, signin)
button_signup.on_event(ButtonClick, signup)
button_accept.on_event(ButtonClick, accept)
# button_cancel.on_event(ButtonClick, cancel)

_env = Environment(loader=FileSystemLoader('app'))
FILE = _env.get_template(os.path.join('templates', 'website.html'))
curdoc().template = FILE

curdoc().add_root(welcome)
curdoc().add_root(button_signin)
curdoc().add_root(button_signup)
curdoc().add_root(username)
curdoc().add_root(password)
curdoc().add_root(row([button_accept, button_cancel]))
curdoc().title = 'TetoPolla'
