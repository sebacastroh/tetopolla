import os
import random
import sqlite3
import datetime

currentDir = os.path.dirname(__file__)
dataPath   = os.path.abspath(os.path.join(currentDir, '..', 'data'))

chileoffset = 4

def choose_random_word():
    with open(os.path.join(dataPath, 'words.txt')) as f:
        words = f.readlines()
    nWords = len(words)
    n      = random.randint(0, nWords-1)
    return words[n].strip()

def signin(username, password):
    
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    try:
        sql = """
                SELECT user_id
                FROM   users
                WHERE
                    user_name = "{username}"
                AND
                    user_password = "{password}";
            """.format(username=username, password=password)

        cur = con.execute(sql)
        user_id = cur.fetchone()[0]
    except:
        user_id = False

    con.close()

    return user_id

def signup(username):
    password = choose_random_word()

    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    try:
        sql = """
            INSERT INTO users (user_name, user_password)
            VALUES
                ("{username}", "{password}");
        """.format(username=username, password=password)

        con.execute(sql)
        con.commit()
    except:
        password = False
    
    con.close()

    return password

def get_tournaments():
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT tournament_id, tournament_name, tournament_season
        FROM   tournaments
        ORDER BY
            tournament_date DESC
        """

    cur = con.execute(sql)
    tournaments = cur.fetchall()
    con.close()

    return tournaments

def get_match(match_id, user_id=None):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT matches.match_id, match_team_code1, match_team_code2, match_score, match_starttime, team1.team_name AS team_name1, team2.team_name AS team_name2, bets.bet_score, match_history, match_additionals, users.user_name
        FROM   matches
        JOIN   teams AS team1
        ON     matches.match_team_code1 = team1.team_code
        JOIN   teams AS team2
        ON     matches.match_team_code2 = team2.team_code
        LEFT JOIN   users
        ON     matches.user_id = users.user_id
        LEFT JOIN bets
        ON     matches.match_id = bets.match_id
        AND    bets.user_id = {user_id}
        WHERE  matches.match_id = {match_id}
    """.format(match_id=match_id, user_id=user_id)

    cur = con.execute(sql)
    match = cur.fetchone()
    con.close()

    return match

def get_matches(tournament_id, starttime=None):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT match_id, match_team_code1, match_team_code2, match_score, match_starttime
        FROM   matches
        WHERE
            tournament_id = {tournament_id}
        """.format(tournament_id=tournament_id)

    if starttime is not None:
        sql += 'AND match_starttime >= "{starttime}"'.format(starttime=starttime)

    sql += """
    ORDER BY match_starttime ASC"""

    cur = con.execute(sql)
    matches = cur.fetchall()
    con.close()

    return matches

def get_bet(user_id, match_id):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT bet_id, bet_score, bet_time
        FROM   bets
        WHERE  
            user_id = {user_id}
        AND
            match_id = {match_id}
    """.format(user_id=user_id, match_id=match_id)

    cur = con.execute(sql)
    bet = cur.fetchone()
    con.close()

    return bet

def get_points(tournament_id, user=None):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT 
            bets.bet_id,
            bets.user_id,
            bets.match_id,
            bets.bet_score,
            matches.match_score,
            matches.match_history,
            matches.match_starttime,
            matches.match_additionals,
            cards.card_name,
            modifiers.modifier_datetime
        FROM
            bets
        JOIN
            matches
        ON
            bets.match_id = matches.match_id
        LEFT JOIN
            modifiers
        ON
            bets.user_id = modifiers.user_id
        AND
            bets.match_id = modifiers.match_id
        LEFT JOIN
            cards
        ON
            modifiers.card_id = cards.card_id
        WHERE
            matches.tournament_id = {tournament_id}
        AND
            matches.match_score IS NOT NULL
    """.format(tournament_id=tournament_id)

    if user is not None:
        sql += 'AND bets.user_id = {user_id}'.format(user_id=user)

    sql += """
    ORDER BY
        bets.user_id
    """

    cur = con.execute(sql)
    bets = cur.fetchall()
    con.close()

    points = {user: 0}
    for bet in bets:
        bet_id, user_id, match_id, bet_score, match_score, match_history, match_starttime, match_additionals, card_name, modifier_datetime = bet

        if points.get(user_id) is None:
            points[user_id] = 0

        bet_points = 0

        if card_name == 'Hincha de cartón':
            b1, b2 = bet_score.split('-')
            bet_score = '-'.join([b2, b1])

        if card_name == 'Profe, la hora':
            first_half  = int(match_additionals.split(';')[0])
            second_half = datetime.datetime.strptime(match_starttime, "%Y-%m-%d %H:%M:%S.%f") + datetime.timedelta(minutes=45+15+first_half)
            stoptime = (datetime.datetime.strptime(modifier_datetime, "%Y-%m-%d %H:%M:%S.%f") - second_half).seconds/60
            if stoptime > 30:
                goals = match_history.split(';')
                n = len(goals)
                match_score = '0-0'
            for k in range(n//2):
                minute = goals[2*k][1:]
                if '+' in minute:
                    minute = sum([int(x) for x in minute.split('+')]) - 45
                else:
                    minute = int(minute) - 45
                if minute > stoptime:
                    break
                match_score = goals[2*k+1]

        if bet_score == match_score:
            bet_points = 5
        else:
            b1, b2 = map(lambda x: int(x), bet_score.split('-'))
            m1, m2 = map(lambda x: int(x), match_score.split('-'))
            if (b1 > b2 and m1 > m2) or (b1 < b2 and m1 < m2) or (b1 == b2 and m1 == m2):
                bet_points = 3
        
        if card_name == 'Doblete':
            bet_points *= 2
        elif card_name == 'Triplete':
            bet_points *= 3
        elif card_name == 'El semental del gol':
            goals = sum(map(lambda x: int(x), match_score.split('-')))
            bet_points += goals
        elif card_name == 'A morir':
            if bet_score == match_score:
                bet_points += 20
            else:
                bet_points -= 10

        points[user_id] += bet_points

    if user is not None:
        return points[user]
    else:
        return points

def make_bet(user_id, match_id, score_team1, score_team2):
    if not isinstance(score_team1, int) or not isinstance(score_team2, int):
        return False

    bet_score = '%i-%i' %(score_team1, score_team2)

    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))

    # Revisamos si el partido empezó o no
    current_datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=chileoffset)
    current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

    sql = """
        SELECT match_starttime
        FROM   matches
        WHERE  match_id = {match_id}
    """.format(match_id=match_id)

    cur = con.execute(sql)
    starttime = cur.fetchone()[0]

    if starttime <= current_datetime:
        con.close()
        return False

    # Chequeamos si la apuesta ya existe o es nueva
    sql = """
        SELECT COUNT(*)
        FROM   bets
        WHERE  user_id = {user_id}
        AND    match_id = {match_id}
    """.format(user_id=user_id, match_id=match_id)

    cur = con.execute(sql)
    count = cur.fetchone()[0]
    
    if count == 0:
        sql = """
            INSERT INTO bets (user_id, match_id, bet_score, bet_time)
            VALUES ({user_id}, {match_id}, "{bet_score}", "{bet_time}")
        """.format(user_id=user_id, match_id=match_id, bet_score=bet_score, bet_time=current_datetime)
    else:
        sql = """
            UPDATE bets
                SET bet_score = "{bet_score}",
                    bet_time  = "{bet_time}"
                WHERE
                    user_id = {user_id}
                AND
                    match_id = {match_id}
        """.format(user_id=user_id, match_id=match_id, bet_score=bet_score, bet_time=current_datetime)

    con.execute(sql)
    con.commit()
    con.close()

    return True

def get_cards():
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT card_id, card_name
        FROM   cards
        """

    cur = con.execute(sql)
    cards = cur.fetchall()
    con.close()

    return cards

def get_card(user_id, tournament_id, card_id):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT COUNT(*), matches.match_starttime, cards.card_in_match
        FROM   modifiers
        JOIN   matches
        ON     modifiers.match_id = matches.match_id
        JOIN   cards
        ON     modifiers.card_id = cards.card_id
        WHERE  modifiers.user_id = {user_id}
        AND    matches.tournament_id = {tournament_id}
        AND    modifiers.card_id = {card_id}
        """.format(user_id=user_id, tournament_id=tournament_id, card_id=card_id)


    cur = con.execute(sql)
    cards = cur.fetchone()
    con.close()

    return cards

def use_card(user_id, card_id, match_id, tournament_id):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))

    # Obtenemos la hora actual
    current_datetime = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=chileoffset)
    current_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')

    # Caso 1: borrar tarjeta
    if match_id == 0:
        sql = """
            SELECT COUNT(*), modifiers.match_id
            FROM   modifiers
            JOIN   matches
            ON     modifiers.match_id = matches.match_id
            AND    matches.tournament_id = {tournament_id}
            WHERE  modifiers.user_id = {user_id}
            AND    modifiers.card_id = {card_id}
            AND    matches.match_starttime > "{current_datetime}"
        """.format(user_id=user_id, card_id=card_id, tournament_id=tournament_id, current_datetime=current_datetime)

        cur = con.execute(sql)
        count, match_id = cur.fetchone()

        if count > 0:
            sql = """
                DELETE FROM modifiers
                WHERE  user_id = {user_id}
                AND    card_id = {card_id}
                AND    match_id = {match_id}
            """.format(user_id=user_id, card_id=card_id, match_id=match_id)

            cur = con.execute(sql)
            con.commit()
            con.close()

            return True
        else:
            con.close()
            return False

    # Caso 2: asignar la tarjeta a un partido

    # Obtenemos si el usuario usó la tarjeta en otro partido
    sql = """
        SELECT COUNT(*), modifiers.match_id
        FROM   modifiers
        JOIN   matches
        ON     modifiers.match_id = matches.match_id
        WHERE  modifiers.user_id = {user_id}
        AND    modifiers.card_id = {card_id}
        AND    matches.tournament_id = {tournament_id}
    """.format(user_id=user_id, card_id=card_id, tournament_id=tournament_id)

    cur = con.execute(sql)
    old_modifier = cur.fetchone()

    # Obtenemos las características de la tarjeta
    sql = """
        SELECT card_name, card_in_match
        FROM   cards
        WHERE  card_id = {card_id}
    """.format(card_id=card_id)

    cur = con.execute(sql)
    card = cur.fetchone()

    # Obtenemos las características del partido
    sql = """
        SELECT match_starttime, match_score
        FROM   matches
        WHERE  match_id = {match_id}
    """.format(match_id=match_id)

    cur = con.execute(sql)
    match = cur.fetchone()

    # Obtenemos si el usuario usó otra tarjeta en el partido
    sql = """
        SELECT COUNT(*)
        FROM   modifiers
        WHERE  user_id = {user_id}
        AND    match_id = {match_id}
        AND    card_id <> {card_id}
    """.format(user_id=user_id, match_id=match_id, card_id=card_id)

    cur = con.execute(sql)
    used_in_another_match = cur.fetchone()

    if used_in_another_match[0] > 0:
        return False    

    # Caso 2.1: la tarjeta solo se puede usar antes del partido
    if card[1] == 0:
        if match[0] <= current_datetime:
            con.close()
            return False
        else:
            if old_modifier[0] == 0:
                sql = """
                    INSERT INTO modifiers (card_id, user_id, match_id, modifier_datetime)
                    VALUES ({card_id}, {user_id}, {match_id}, "{modifier_datetime}")
                """.format(card_id=card_id, user_id=user_id, match_id=match_id, modifier_datetime=current_datetime)
            else:
                sql = """
                    UPDATE modifiers
                    SET match_id = {match_id},
                        modifier_datetime = "{modifier_datetime}"
                    WHERE
                        user_id = {user_id}
                    AND
                        match_id = {old_match_id}
                    AND card_id = {card_id}
                """.format(card_id=card_id, user_id=user_id, match_id=match_id, old_match_id=old_modifier[1], modifier_datetime=current_datetime)

            cur = con.execute(sql)
            con.commit()
            con.close()

            return True
    else:
    # Caso 2.2: la tarjeta puede ser usada durante el partido
        if old_modifier[0] == 0:
                sql = """
                    INSERT INTO modifiers (card_id, user_id, match_id, modifier_datetime)
                    VALUES ({card_id}, {user_id}, {match_id}, "{modifier_datetime}")
                """.format(card_id=card_id, user_id=user_id, match_id=match_id, modifier_datetime=current_datetime)
        else:
            # Si la tarjeta está siendo usada en un partido que se está jugando, no se puede cambiar
            sql = """
                SELECT match_starttime
                FROM   matches
                WHERE  match_id = {match_id}
            """.format(match_id=old_modifier[1])
            cur = con.execute(sql)
            match_starttime = cur.fetchone()[0]
            
            if current_datetime > match_starttime:
                con.close()
                return False
            else:
                sql = """
                    UPDATE modifiers
                    SET match_id = {match_id},
                        modifier_datetime = "{modifier_datetime}"
                    WHERE
                        user_id = {user_id}
                    AND
                        match_id = {old_match_id}
                    AND card_id = {card_id}
                """.format(card_id=card_id, user_id=user_id, match_id=match_id, old_match_id=old_modifier[1], modifier_datetime=current_datetime)

        cur = con.execute(sql)
        con.commit()
        con.close()

        return True


def get_user_cards(user_id, tournament_id):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT cards.card_name, matches.match_team_code1, matches.match_team_code2
        FROM   modifiers
        JOIN   matches
        ON     modifiers.match_id = matches.match_id
        JOIN   cards
        ON     modifiers.card_id = cards.card_id
        WHERE  modifiers.user_id = {user_id}
        AND    matches.tournament_id = {tournament_id}
        """.format(user_id=user_id, tournament_id=tournament_id)

    cur = con.execute(sql)
    cards = cur.fetchall()
    con.close()

    return cards

def get_usernames():
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
        SELECT user_id, user_name
        FROM   users
    """

    cur = con.execute(sql)
    users = cur.fetchall()
    con.close()

    return users

def get_bets(user_id, tournament_id):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
    SELECT match_team_code1, match_team_code2, bet_score, match_score
    FROM bets
    JOIN matches
    ON   bets.match_id = matches.match_id
    WHERE bets.user_id = {user_id}
    AND   matches.tournament_id = {tournament_id}
    ORDER BY matches.match_starttime
    """.format(user_id=user_id, tournament_id=tournament_id)

    cur = con.execute(sql)
    bets = cur.fetchall()
    con.close()

    return bets

def get_teams(tournament_id):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
    SELECT teams.team_code, teams.team_name
    FROM teams
    JOIN tournaments_teams
    ON   teams.team_id = tournaments_teams.team_id
    WHERE tournaments_teams.tournament_id = {tournament_id}
    ORDER BY teams.team_name
    """.format(tournament_id=tournament_id)

    cur = con.execute(sql)
    teams = cur.fetchall()
    con.close()

    return teams

def get_rounds():
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    sql = """
    SELECT round_code, round_name
    FROM   rounds
    """

    cur = con.execute(sql)
    rounds = cur.fetchall()
    con.close()

    return rounds

def add_match(user_id, tournament_id, match_team_code1, match_team_code2, match_starttime, match_phase):

    if match_team_code1 == '' or match_team_code2 == '' or match_team_code1 == match_team_code2:
        return False

    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))
    
    sql = """
    SELECT COUNT(*)
    FROM   matches
    WHERE  match_team_code1 = "{match_team_code1}"
    AND    match_team_code2 = "{match_team_code2}"
    AND    tournament_id    = {tournament_id}
    AND    match_phase      = "{match_phase}"
    """.format(tournament_id=tournament_id, match_team_code1=match_team_code1, match_team_code2=match_team_code2, match_phase=match_phase)

    cur = con.execute(sql)
    count = cur.fetchone()[0]

    if count > 0:
        con.close()
        return False

    try:
        sql = """
        INSERT INTO matches (match_team_code1, match_team_code2, match_starttime, match_phase, tournament_id)
        VALUES ("{match_team_code1}", "{match_team_code2}", "{match_starttime}", "{match_phase}", {tournament_id})
        """.format(tournament_id=tournament_id, match_team_code1=match_team_code1, match_team_code2=match_team_code2, match_phase=match_phase, match_starttime=match_starttime)

        con.execute(sql)
        con.commit()
        con.close()

        return True
    except:
        con.close()
        return False

def update_result(user_id, match_id, match_history, match_additionals, match_score):
    con = sqlite3.connect(os.path.join(dataPath, 'tetopolla.db'))

    sql = """
    UPDATE matches
    SET    match_history = "{match_history}",
           match_additionals = "{match_additionals}",
           match_score = "{match_score}",
           user_id = {user_id}
    WHERE  match_id = {match_id}
    """.format(match_id=match_id, match_history=match_history, match_additionals=match_additionals, match_score=match_score, user_id=user_id)

    con.execute(sql)
    con.commit()
    con.close()