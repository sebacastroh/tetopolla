import os

from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Slider, TextInput
from bokeh.models.widgets import Button

from jinja2 import Environment, FileSystemLoader

username = TextInput(title='Nombre de usuario', name='username')
password = TextInput(title='Contraseña', name='password')

button_login   = Button(label='Iniciar sesión', button_type='success', sizing_mode='stretch_width', align='end', name='login')
button_matches = Button(label='Partidos', button_type='success', sizing_mode='stretch_width', align='end')
button_cards   = Button(label='Mis tarjetas', button_type='success', sizing_mode='stretch_width', align='end')

_env = Environment(loader=FileSystemLoader('app'))
FILE = _env.get_template(os.path.join('templates', 'website.html'))
curdoc().template = FILE

curdoc().add_root(username)
curdoc().add_root(password)
curdoc().add_root(button_login)
curdoc().title = 'TetoPolla'
