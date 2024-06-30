import os
import helpers
import sqlite3
import datetime

from bokeh.io import curdoc
from bokeh.events import ButtonClick
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DatetimePicker, Div, Slider, TextInput
from bokeh.models.widgets import Button, Select, NumericInput

from jinja2 import Environment, FileSystemLoader

# Variables globales
method  = None
user_id = None
chileoffset = 4
matches = []

#================#
#  HERRAMIENTAS  #
#================#

##############
##  VARIOS  ##
##############
div_message   = Div(text='', visible=False)
button_accept = Button(label='Aceptar', button_type='success', align='end', visible=False)
button_cancel = Button(label='Cancelar', button_type='danger', align='end', visible=False)

########################
##  PÁGINA DE INICIO  ##
########################
button_signin = Button(label='Iniciar sesión', button_type='success', align='end', name='signin', visible=False)
button_signup = Button(label='Crear cuenta'  , button_type='primary', align='end', name='singup', visible=False)

#######################
##  CREACIÓN CUENTA  ##
#######################
username = TextInput(title='Nombre de usuario', name='username', visible=False)

########################
##  INICIO DE SESIÓN  ##
########################
password = TextInput(title='Contraseña', name='password', visible=False)

########################
##  PÁGINA PRINCIPAL  ##
########################
button_rankings    = Button(label='Rankings', button_type='primary', align='end', visible=False)
button_tournaments = Button(label='Torneos', button_type='primary', align='end', visible=False)
button_rules       = Button(label='Reglas', button_type='primary', align='end', visible=False)

#########################
##  PÁGINA DE TORNEOS  ##
#########################
select_tournament = Select(title='', visible=False, sizing_mode='stretch_width')
div_tournaments   = Div(text='', visible=False)
button_bets       = Button(label='Apostar partidos', button_type='primary', align='end', visible=False)
button_cards      = Button(label='Usar tarjetas', button_type='primary', align='end', visible=False)
button_past_bets  = Button(label='Historial de apuestas', button_type='primary', align='end', visible=False)
button_settings   = Button(label='Configuración', button_type='primary', align='end', visible=False)

##########################
##  PÁGINA DE APUESTAS  ##
##########################
select_match = Select(title='Selecciona un partido', visible=False, sizing_mode='stretch_width')
div_team1    = Div(text='', visible=False, styles={'width': '20%'})
input_team1  = NumericInput(visible=False, styles={'width': '15%'})
div_vs       = Div(text='<b>vs</b>', visible=False, styles={'width': '15%', 'margin-left': '7.5%'})
input_team2  = NumericInput(visible=False, styles={'width': '15%'})
div_team2    = Div(text='', visible=False, styles={'width': '20%'})
row_match    = row(children=[div_team1, input_team1, div_vs, input_team2, div_team2], sizing_mode='stretch_width')
div_post_bet = Div(text='', visible=False)

##########################
##  PÁGINA DE TARJETAS  ##
##########################
current_cards         = Div(text='', visible=False)
select_card           = Select(title='Selecciona una tarjeta', visible=False, sizing_mode='stretch_width')
select_match_for_card = Select(title='Selecciona un partido', visible=False, sizing_mode='stretch_width')
div_post_card         = Div(text='', visible=False)

#########################################
##  PÁGINA DE CONFIGURACIÓN DE TORNEO  ##
#########################################
button_add_match        = Button(label='Crear partido en el torneo', button_type='primary', align='end', visible=False)
button_set_match_result = Button(label='Agregar o modificar resultados', button_type='primary', align='end', visible=False)

###############################
##  PÁGINA DE NUEVO PARTIDO  ##
###############################
select_team1      = Select(title='Selecciona el primer equipo', visible=False, sizing_mode='stretch_width')
select_team2      = Select(title='Selecciona el segundo equipo', visible=False, sizing_mode='stretch_width')
select_datetime   = DatetimePicker(title='Selecciona hora y fecha del partido (hora de Chile)', visible=False, sizing_mode='stretch_width')
select_phase      = Select(title='Selecciona la fase', visible=False, sizing_mode='stretch_width')
div_post_settings = Div(text='', visible=False)

############################
##  PÁGINA DE RESULTADOS  ##
############################
select_match_for_settings = Select(title='Selecciona un partido', visible=False, sizing_mode='stretch_width')
text_history     = TextInput(title='Escribe la historia del partido', placeholder='Ej: M15;1-0;M45+2;2-0;M75;2-1', visible=False, sizing_mode='stretch_width')
text_additionals = TextInput(title='Indica los minutos adicionados', placeholder='Ej: 1;5', visible=False, sizing_mode='stretch_width')
text_results     = TextInput(title='Resultado final del partido', placeholder='Ej: 2-1', visible=False, sizing_mode='stretch_width')

##########################
##  PÁGINA DE RANKINGS  ##
##########################
select_tournament_for_ranking = Select(title='', visible=False, sizing_mode='stretch_width')
div_ranking                   = Div(text='', visible=False)

#==========#
#  VISTAS  #
#==========#
def hide_all():
    div_message.update(visible=False)
    button_accept.update(visible=False)
    button_cancel.update(visible=False)
    button_signin.update(visible=False)
    button_signup.update(visible=False)
    username.update(visible=False)
    password.update(visible=False)
    button_rankings.update(visible=False)
    button_tournaments.update(visible=False)
    button_rules.update(visible=False)
    select_tournament.update(visible=False)
    div_tournaments.update(visible=False)
    button_bets.update(visible=False)
    button_cards.update(visible=False)
    button_past_bets.update(visible=False)
    button_settings.update(visible=False)
    select_match.update(visible=False)
    div_team1.update(visible=False)
    input_team1.update(visible=False)
    div_vs.update(visible=False)
    input_team2.update(visible=False)
    div_team2.update(visible=False)
    div_post_bet.update(visible=False)
    current_cards.update(visible=False)
    select_card.update(visible=False)
    select_match_for_card.update(visible=False)
    div_post_card.update(visible=False)
    select_tournament_for_ranking.update(visible=False)
    div_ranking.update(visible=False)
    button_add_match.update(visible=False)
    button_set_match_result.update(visible=False)
    select_team1.update(visible=False)
    select_team2.update(visible=False)
    select_datetime.update(visible=False)
    select_phase.update(visible=False)
    div_post_settings.update(visible=False)
    select_match_for_settings.update(visible=False)
    text_history.update(visible=False)
    text_additionals.update(visible=False)
    text_results.update(visible=False)

def view_init():
    hide_all()
    div_message.update(text='<h1>¡Bienvenido a la TetoPolla!</h1>', visible=True)
    button_signin.update(visible=True)
    button_signup.update(visible=True)

def view_signup():
    global method

    hide_all()

    text_signup = '<h1>Ingresa el nombre de usuario que deseas utilizar. Se te ' + \
        'asignará una contraseña aleatoria que no podrá ser cambiada. ¡No la olvides!</h1>'
    div_message.update(text=text_signup, visible=True)
    button_signin.update(visible=False)
    button_signup.update(visible=False)
    username.update(visible=True)
    button_accept.update(visible=True)
    button_cancel.update(visible=True)

    method = 'signup'

def view_signin():
    global method

    hide_all()    
    div_message.update(text='<h1>Ingresa tu nombre de usuario y contraseña</h1>', visible=True)
    button_signin.update(visible=False)
    button_signup.update(visible=False)
    username.update(visible=True)
    password.update(visible=True)
    button_accept.update(visible=True)
    button_cancel.update(visible=True)

    method = 'signin'

def view_main_page():
    hide_all()
    div_message.update(text='<h1>Selecciona una opción</h1>', visible=True)
    button_rankings.update(visible=True)
    button_tournaments.update(visible=True)
    button_rules.update(visible=True)

def view_tournaments():
    global method
    method = 'tournament'
    hide_all()
    
    div_message.update(text='<h1>Selecciona un torneo</h1>', visible=True)
    tournaments = helpers.get_tournaments()
    select_tournament.update(
        options=[(tournament_id, tournament_name + ' - ' + tournament_season) for tournament_id, tournament_name, tournament_season in tournaments],
        visible=True
    )
    button_cancel.update(visible=True)

def view_rules():
    pass

def load_tournament(attr, old, new):
    tournament_id = select_tournament.value
    if tournament_id == '':
        return
    
    current_datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=chileoffset)
    current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

    points  = helpers.get_points(tournament_id, user_id)
    matches = helpers.get_matches(tournament_id)

    k = 0
    next_matches = ''
    for match in matches:
        if match[4] >= current_datetime:
            if k == 0:
                next_matches += '<ul>'
            next_matches += '<li><h2>' + match[1] + ' vs ' + match[2] + ' (' + match[4][:16] + ')</h2></li>'
            k += 1
        if k == 3:
            break
    if k > 0:
        next_matches += '</ul>'
    else:
        next_matches = 'No quedan partidos por jugar'

    html_tournaments = """
    <h1>Puntos obtenidos: {points}</h1>

    <h1>Próximos partidos</h1>

    {next_matches}
    """.format(points=points, next_matches=next_matches)
    div_tournaments.update(text=html_tournaments, visible=True)
    button_bets.update(visible=True)
    button_cards.update(visible=True)
    button_past_bets.update(visible=True)
    button_settings.update(visible=True)

def view_bets():
    global method

    method = 'bets'

    hide_all()

    bets_header = '<h3>Escoge un partido para realizar una apuesta. La apuesta no se guarda hasta que hagas clic en "Aceptar". ' + \
        'Las tarjetas se asocian en la sección "Tarjetas".</h3>'
    div_message.update(text=bets_header, visible=True)

    tournament_id = select_tournament.value

    current_datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=chileoffset)
    current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

    matches = helpers.get_matches(tournament_id, current_datetime)

    select_match.update(
        options=[(match[0], match[1] + ' vs ' + match[2]) for match in matches],
        visible=True
    )

    button_accept.update(visible=True)
    button_cancel.update(visible=True)

def load_match(attr, old, new):
    global matches

    if select_tournament.value == '':
        return

    div_post_bet.update(visible=False)

    match_id = select_match.value

    current_datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=chileoffset)
    current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

    match = helpers.get_match(match_id, user_id)

    if isinstance(match[7], str):
        b1 = int(match[7].split('-')[0])
        b2 = int(match[7].split('-')[1])
    else:
        b1 = None
        b2 = None

    if match[4] > current_datetime:
        div_team1.update(text=match[5], visible=True)
        input_team1.update(value=b1, visible=True, disabled=False)
        div_vs.update(visible=True)
        input_team2.update(value=b2, visible=True, disabled=False)
        div_team2.update(text=match[6], visible=True)
    else:
        div_team1.update(text=match[5], visible=True)
        input_team1.update(value=b1, visible=True, disabled=True)
        div_vs.update(visible=True)
        input_team2.update(value=b2, visible=True, disabled=True)
        div_team2.update(text=match[6], visible=True)

def view_cards():
    global method
    hide_all()
    method = 'cards'

    cards_header = '<h3>Selecciona una tarjeta. Si la tarjeta ya fue usada, y el partido empezó, no la puedes cambiar.' + \
    ' Si todavía no empieza, puedes borrarla (primera opción) o escoger otro partido. Las tarjetas que se usan ' + \
    'dentro de un partido no se pueden cancelar.</h3>'
    div_message.update(text=cards_header, visible=True)

    tournament_id = select_tournament.value
    cards = helpers.get_cards()
    user_cards = helpers.get_user_cards(user_id, tournament_id)

    list_cards = '<ul>'
    k = 0
    for user_card in user_cards:
        list_cards += '<li><b>' + user_card[0] + '</b>: ' + user_card[1] + ' vs ' + user_card[2] + '</li>' 
        k += 1
    list_cards += '</ul>'

    if k > 0:
        current_cards.update(text=list_cards, visible=True)
    else:
        current_cards.update(visible=False)

    select_card.update(
        options=[(card_id, card_name) for card_id, card_name in cards if card_name not in ["Toby Vega", "Todos al ataque"]],
        visible=True
    )

    button_cancel.update(visible=True)

def update_user_cards():
    user_cards = helpers.get_user_cards(user_id, select_tournament.value)

    list_cards = '<ul>'
    k = 0
    for user_card in user_cards:
        list_cards += '<li><b>' + user_card[0] + '</b>: ' + user_card[1] + ' vs ' + user_card[2] + '</li>' 
        k += 1
    list_cards += '</ul>'

    if k > 0:
        current_cards.update(text=list_cards, visible=True)
    else:
        current_cards.update(visible=False)

def load_card(attr, old, new):
    if select_card.value == '':
        return

    tournament_id = select_tournament.value
    select_match_for_card.update(visible=False)
    div_post_card.update(visible=False)
    used_card = helpers.get_card(user_id, tournament_id, select_card.value)
    matches = helpers.get_matches(tournament_id)
    select_match_for_card.update(
        options=[(0, "Borrar")] + [(match[0], match[1] + ' vs ' + match[2]) for match in matches if match[3] is None],
        visible=True
    )
    button_accept.update(visible=True)


def update_card(attr, old, new):
    div_post_card.update(visible=False)

def view_past_bets():
    global method
    method = 'bets'
    hide_all()

    bets = helpers.get_bets(user_id, select_tournament.value)

    bets_div = '<h1>A continuación se muestran las apuestas que has realizado junto al resultado final del partido</h1> <ul>'
    for bet in bets:
        match_team_code1, match_team_code2, bet_score, match_score = bet
        if match_score is None:
            match_score = 'Por jugar'
        bets_div += '<li>' + match_team_code1 + ' vs ' + match_team_code2 + ': ' + bet_score + ' (' + match_score + ')</li>'
    bets_div += '</ul>'

    div_message.update(text=bets_div, visible=True)
    button_cancel.update(visible=True)

def view_rankings():
    global method
    method = 'ranking'
    hide_all()
    
    div_message.update(text='<h1>Selecciona un torneo</h1>', visible=True)
    tournaments = helpers.get_tournaments()
    select_tournament_for_ranking.update(
        options=[(tournament_id, tournament_name + ' - ' + tournament_season) for tournament_id, tournament_name, tournament_season in tournaments],
        visible=True
    )

    button_cancel.update(visible=True)

def load_ranking(attr, old, new):

    if select_tournament_for_ranking.value == '':
        return

    points    = helpers.get_points(select_tournament_for_ranking.value)
    usernames = helpers.get_usernames()

    users = {}
    for user in usernames:
        user_id = user[0]
        if points.get(user_id) is None:
            continue

        users[user_id] = [user[1], points[user_id]]

    positions = [[users[y[1]][0], users[y[1]][1]] for y in reversed(sorted([(users[x][1], x) for x in users.keys()]))]

    ranking = '<ul>'
    for i, position in enumerate(positions):
        ranking += '<li>%i. %s: %i puntos</li>' %(i+1, position[0], position[1])
    ranking += '</ul>'

    div_ranking.update(text=ranking, visible=True)


def view_settings():
    hide_all()
    global method
    method = 'settings'

    div_message.update(text='<h2>Selecciona una opción para configurar el torneo. Esto afectará a todos los jugadores. ' + \
        'La fecha, hora y el nombre del usuario responsable quedará registrado, sé responsable, pasemos un buen rato ;-).</h2>', visible=True)

    button_add_match.update(visible=True)
    button_set_match_result.update(visible=True)
    button_cancel.update(visible=True)

def view_new_match():
    hide_all()
    global method
    method = 'new_match'

    div_message.update(text='<h2>Selecciona los dos equipos que jugarán, la fase y haz clic en Aceptar. Si el partido ya existe se te avisará</h2>', visible=True)

    teams  = helpers.get_teams(select_tournament.value)
    rounds = helpers.get_rounds()

    select_team1.update(options=[(team_code, team_name) for team_code, team_name in teams], visible=True)
    select_team2.update(options=[(team_code, team_name) for team_code, team_name in teams], visible=True)
    select_datetime.update(visible=True)
    select_phase.update(options=[(round_code, round_name) for round_code, round_name in rounds], visible=True)

    button_accept.update(visible=True)
    button_cancel.update(visible=True)

def view_set_result():
    hide_all()
    global method
    method = 'set_result'

    div_message.update(text='<h2>Selecciona un partido. Ahí podrás modificar su historia, minutos adicionados y resultado final.' + \
        ' Todos los inputs deben ser sin espacios.</h2>', visible=True)

    matches = helpers.get_matches(select_tournament.value)
    select_match_for_settings.update(
        options=[(match[0], match[1] + ' vs ' + match[2]) for match in matches],
        visible=True
    )

    button_cancel.update(visible=True)

def load_match_result(attr, old, new):
    
    if select_match_for_settings.value == '':
        return

    match = helpers.get_match(select_match_for_settings.value, "NULL")

    match_id, match_team_code1, match_team_code2, match_score, match_starttime, team_name1, team_name2, bet_score, match_history, match_additionals, match_user_name = match

    if match_user_name is not None:
        div_message.update(text='<h2>Selecciona un partido. Ahí podrás modificar su historia, minutos adicionados y resultado final.' + \
        ' Todos los inputs deben ser sin espacios.</h2> <h3>Información ingresada por %s</h3>' %match_user_name, visible=True)
    else:
        div_message.update(text='<h2>Selecciona un partido. Ahí podrás modificar su historia, minutos adicionados y resultado final.' + \
        ' Todos los inputs deben ser sin espacios.</h2>', visible=True)

    text_history.update(value=match_history if match_history else '', visible=True)
    text_additionals.update(value=match_additionals if match_additionals else '', visible=True)
    text_results.update(value=match_score if match_score else '', visible=True)

    button_accept.update(visible=True)


#===========#
#  EVENTOS  #
#===========#

def accept():
    global method, user_id

    status = False
    if method == 'signin':
        status = helpers.signin(username.value.strip(), password.value.strip())
        if status:
            user_id = status
            view_main_page()
        else:
            div_message.update(text='Ha ocurrido un error, revisa tu usuario y contraseña')

    elif method == 'signup':
        status = helpers.signup(username.value.strip())
        if status:
            hide_all()
            div_message.update(text='Operación exitosa. Tu contraseña es: ' + status, visible=True)
            button_accept.update(visible=True)
            method = 'goToInit'
        else:
            div_message.update(text='Ha ocurrido un error, puede ser que el nombre de usuario ya esté ocupado')

    elif method == 'goToInit':
        view_init()

    elif method == 'bets':
        status = helpers.make_bet(user_id, select_match.value, input_team1.value, input_team2.value)
        if status:
            div_post_bet.update(text='<h3>Apuesta registrada exitosamente</h3>', visible=True)
        else:
            div_post_bet.update(text='<h3>No se pudo registrar la apuesta. Asegurate de haber ingresado un valor a cada equipo. Recuerda: si el partido empezó, no puedes registrar una apuesta</h3>', visible=True)

    elif method == 'cards':
        status = helpers.use_card(user_id, select_card.value, select_match_for_card.value, select_tournament.value)
        if status:
            div_post_card.update(text='<h3>Tarjeta activada o actualizada correctamente</h3>', visible=True)
            update_user_cards()
        else:
            div_post_card.update(text='<h3>No se puede usar o actualizar la tarjeta. Recuerda que si el partido ya empezó o terminó no la puedes desactivar.</h3>', visible=True)

    elif method == 'new_match':
        if select_team1.value is not None and select_team2.value is not None and select_datetime.value is not None and select_phase.value is not None:
            status = helpers.add_match(user_id, select_tournament.value, select_team1.value, select_team2.value,
                datetime.datetime.fromtimestamp(select_datetime.value/1000).strftime('%Y-%m-%d %H:%M:%S.%f'), select_phase.value)

        if status:
            div_post_settings.update(text='<h3>Partido registrado exitosamente</h3>', visible=True)
        else:
            div_post_settings.update(text='<h3>Ha habido un error. Verifica que el mismo partido no haya sido registrado antes.</h3>', visible=True)

    elif method == 'set_result':
        status = helpers.update_result(user_id, select_match_for_settings.value, text_history.value, text_additionals.value, text_results.value)
        div_post_settings.update(text='<h3>Partido actualizado exitosamente</h3>', visible=True)



def cancel():
    global method

    if method == 'signin':
        view_init()
    elif method == 'signup':
        view_init()
    elif method == 'tournament':
        select_tournament.update(value='')
        view_main_page()
    elif method == 'bets':
        select_tournament.update(value='')
        select_match.update(value='')
        view_tournaments()
    elif method == 'cards':
        select_tournament.update(value='')
        select_card.update(value='')
        select_match_for_card.update(value='')
        view_tournaments()
    elif method == 'ranking':
        select_tournament_for_ranking.update(value='')
        view_main_page()
    elif method == 'settings':
        select_tournament.update(value='')
        view_tournaments()
    elif method == 'new_match' or method == 'set_result':
        view_settings()

button_signin.on_event(ButtonClick, view_signin)
button_signup.on_event(ButtonClick, view_signup)
button_accept.on_event(ButtonClick, accept)
button_cancel.on_event(ButtonClick, cancel)
button_rankings.on_event(ButtonClick, view_rankings)
button_tournaments.on_event(ButtonClick, view_tournaments)
select_tournament.on_change('value', load_tournament)
button_bets.on_event(ButtonClick, view_bets)
select_match.on_change('value', load_match)
button_rules.on_event(ButtonClick, view_rules)
button_cards.on_event(ButtonClick, view_cards)
button_past_bets.on_event(ButtonClick, view_past_bets)
select_card.on_change('value', load_card)
select_match_for_card.on_change('value', update_card)
select_tournament_for_ranking.on_change('value', load_ranking)
button_settings.on_event(ButtonClick, view_settings)
button_add_match.on_event(ButtonClick, view_new_match)
button_set_match_result.on_event(ButtonClick, view_set_result)
select_match_for_settings.on_change('value', load_match_result)

view_init()

#############

_env = Environment(loader=FileSystemLoader('app'))
FILE = _env.get_template(os.path.join('templates', 'website.html'))
curdoc().template = FILE

curdoc().add_root(div_message)
curdoc().add_root(button_signin)
curdoc().add_root(button_signup)
curdoc().add_root(username)
curdoc().add_root(password)
curdoc().add_root(button_rankings)
curdoc().add_root(button_tournaments)
curdoc().add_root(button_rules)
curdoc().add_root(select_tournament)
curdoc().add_root(div_tournaments)
curdoc().add_root(button_bets)
curdoc().add_root(button_cards)
curdoc().add_root(button_past_bets)
curdoc().add_root(select_match)
curdoc().add_root(row_match)
curdoc().add_root(div_post_bet)
curdoc().add_root(current_cards)
curdoc().add_root(select_card)
curdoc().add_root(select_match_for_card)
curdoc().add_root(div_post_card)

curdoc().add_root(button_settings)
curdoc().add_root(button_add_match)
curdoc().add_root(select_team1)
curdoc().add_root(select_team2)
curdoc().add_root(select_datetime)
curdoc().add_root(select_phase)

curdoc().add_root(select_match_for_settings)
curdoc().add_root(text_history)
curdoc().add_root(text_additionals)
curdoc().add_root(text_results)

curdoc().add_root(div_post_settings)

curdoc().add_root(button_set_match_result)

curdoc().add_root(select_tournament_for_ranking)
curdoc().add_root(div_ranking)

curdoc().add_root(row([button_accept, button_cancel]))
curdoc().title = 'TetoPolla'
