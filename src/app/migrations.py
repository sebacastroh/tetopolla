import os
import json
import sqlite3

currentDir = os.path.dirname(__file__)
migrPath   = os.path.join(currentDir, 'migrations')

con = sqlite3.connect(os.path.join('data', 'tetopolla.db'))

# Tabla de usuarios
sql = """
    CREATE TABLE IF NOT EXISTS users
    ( user_id       INTEGER PRIMARY KEY AUTOINCREMENT
    , user_name     TEXT NOT NULL UNIQUE
    , user_password TEXT NOT NULL
    ) """
con.execute(sql)
con.commit()

# Tabla de equipos
sql = """
    CREATE TABLE IF NOT EXISTS teams
    ( team_id      INTEGER PRIMARY KEY AUTOINCREMENT
    , team_name    TEXT NOT NULL
    , team_code    TEXT NOT NULL
    , UNIQUE(team_name, team_code)
    ) """
con.execute(sql)
con.commit()

# Tabla de torneos
sql = """
    CREATE TABLE IF NOT EXISTS tournaments
    ( tournament_id     INTEGER PRIMARY KEY AUTOINCREMENT
    , tournament_name   TEXT NOT NULL
    , tournament_season TEXT NOT NULL
    , tournament_date   TEXT NOT NULL
    , UNIQUE(tournament_name, tournament_season)
    ) """
con.execute(sql)
con.commit()

# Tabla de equipos en un torneo
sql = """
    CREATE TABLE IF NOT EXISTS tournaments_teams
    ( tournament_id INTEGER NOT NULL
    , team_id       INTEGER NOT NULL
    , UNIQUE(tournament_id, team_id)
    , FOREIGN KEY(tournament_id) REFERENCES tournaments(tournament_id)
    , FOREIGN KEY(team_id) REFERENCES teams(team_id)
    ) """
con.execute(sql)
con.commit()

# Tabla de partidos
sql = """
    CREATE TABLE IF NOT EXISTS matches
    ( match_id         INTEGER PRIMARY KEY AUTOINCREMENT
    , match_team_code1 TEXT NOT NULL
    , match_team_code2 TEXT NOT NULL
    , match_starttime  TEXT NOT NULL
    , match_endtime    TEXT
    , match_score      TEXT
    , match_phase      TEXT NOT NULL
    , match_penalties  INTEGER
    , match_winner     INTEGER
    , match_history    TEXT
    , match_additionals TEXT
    , tournament_id    INTEGER NOT NULL
    , user_id          INTEGER
    , FOREIGN KEY(tournament_id) REFERENCES tournaments(tournament_id)
    , FOREIGN KEY(user_id) REFERENCES users(user_id)
    ) """
con.execute(sql)
con.commit()

# Tabla de tarjetas
sql = """
    CREATE TABLE IF NOT EXISTS cards
    ( card_id          INTEGER PRIMARY KEY AUTOINCREMENT
    , card_name        TEXT NOT NULL
    , card_description TEXT
    , card_in_match    INTEGER NOT NULL
    , UNIQUE(card_name)
    ) """
con.execute(sql)
con.commit()

# Tabla de apuestas
sql = """
    CREATE TABLE IF NOT EXISTS bets
    ( bet_id     INTEGER PRIMARY KEY AUTOINCREMENT
    , user_id    INTEGER NOT NULL
    , match_id   INTEGER NOT NULL
    , bet_score  TEXT NOT NULL
    , bet_time   TEXT NOT NULL
    , bet_points INTEGER
    , FOREIGN KEY(user_id) REFERENCES users(user_id)
    , FOREIGN KEY(match_id) REFERENCES matches(match_id)
    , UNIQUE(user_id, match_id)
    ) """
con.execute(sql)
con.commit()

# Tabla de modificadores
sql = """
    CREATE TABLE IF NOT EXISTS modifiers
    ( card_id           INTEGER NOT NULL
    , user_id           INTEGER NOT NULL
    , match_id          INTEGER NOT NULL
    , modifier_datetime TEXT
    , FOREIGN KEY(card_id) REFERENCES cards(card_id)
    , FOREIGN KEY(user_id) REFERENCES users(user_id)
    , FOREIGN KEY(match_id) REFERENCES matches(match_id)
    , UNIQUE(user_id, match_id)
    ) """
con.execute(sql)
con.commit()

# Tabla de fases
sql = """
    CREATE TABLE IF NOT EXISTS rounds
    ( round_id   INTEGER PRIMARY KEY AUTOINCREMENT
    , round_name TEXT NOT NULL
    , round_code TEXT NOT NULL
    , UNIQUE(round_code)
    ) """

con.execute(sql)
con.commit()

# Tabla de migraciones
sql = """
    CREATE TABLE IF NOT EXISTS migrations
    ( migration_id   INTEGER PRIMARY KEY AUTOINCREMENT
    , migration_name TEXT NOT NULL
    ) """
con.execute(sql)
con.commit()

# Carga basal
with open(os.path.join(migrPath, 'base', 'cards.json')) as f:
    cards = json.load(f)

for card in cards.get('cards'):
    sql = """
        INSERT INTO cards (card_name, card_description, card_in_match)
        VALUES ("{card_name}", "{card_description}", {card_in_match})
    """.format(card_name=card.get('name'), card_description=card.get('description'), card_in_match=int(card.get('in_match')))
    try:
        con.execute(sql)
        con.commit()
    except:
        pass

with open(os.path.join(migrPath, 'base', 'rounds.json')) as f:
    rounds = json.load(f)

for round_ in rounds.get('rounds'):
    sql = """
        INSERT INTO rounds (round_name, round_code)
        VALUES ("{round_name}", "{round_code}")
    """.format(round_name=round_.get('name'), round_code=round_.get('code'))
    try:
        con.execute(sql)
        con.commit()
    except:
        pass

# Carga de equipos, torneos y partidos
migrations = os.listdir(os.path.join(migrPath, 'tournaments'))
for migration in sorted(migrations):
    if not migration.endswith('.txt'):
        continue

    sql = """
        SELECT COUNT(*)
        FROM   migrations
        WHERE  migration_name = "{migration}"
    """.format(migration=migration)

    cur   = con.execute(sql)
    count = cur.fetchone()[0]

    if count > 0:
        continue

    with open(os.path.join(migrPath, 'tournaments', migration)) as f:
        lines = f.readlines()

    team_codes = []

    for line in lines:
        if line.startswith('# Torneo'):
            section = 'tournament'
            continue
        elif line.startswith('# Equipos'):
            section = 'teams'
            continue
        elif line.startswith('# Partidos'):
            section = 'matches'
            continue
        elif line.strip() == '':
            continue

        if section == 'tournament':
            tournament_name, tournament_season, tournament_date = line.strip().split(',')

            sql_tournament = """
                INSERT INTO tournaments (tournament_name, tournament_season, tournament_date)
                VALUES ("{tournament_name}", "{tournament_season}", "{tournament_date}")
            """.format(tournament_name=tournament_name, tournament_season=tournament_season, tournament_date=tournament_date)

            try:
                con.execute(sql_tournament)
                con.commit()
            except:
                pass

            sql = """
                SELECT tournament_id
                FROM   tournaments
                WHERE
                    tournament_name = "{tournament_name}"
                AND
                    tournament_season = "{tournament_season}"
            """.format(tournament_name=tournament_name, tournament_season=tournament_season)

            cur = con.execute(sql)
            tournament_id = cur.fetchone()[0]

        elif section == 'teams':
            team_name, team_code = line.strip().split(',')
            sql_team = """
                INSERT INTO teams (team_name, team_code)
                VALUES
                    ("{team_name}", "{team_code}")
            """.format(team_name=team_name, team_code=team_code)

            con.execute(sql_team)
            con.commit()
            team_codes.append(team_code)

        elif section == 'matches':
            match_team_code1, match_team_code2, match_starttime, match_phase = line.strip().split(',')

            sql_match = """
                INSERT INTO matches (match_team_code1, match_team_code2, match_starttime, match_phase, tournament_id)
                VALUES
                    ("{match_team_code1}", "{match_team_code2}", "{match_starttime}", "{match_phase}", {tournament_id})
            """.format(match_team_code1=match_team_code1, match_team_code2=match_team_code2,
                match_starttime=match_starttime, match_phase=match_phase, tournament_id=tournament_id)
            
            con.execute(sql_match)
            con.commit()

    for team_code in team_codes:
        sql = """
        SELECT team_id
        FROM   teams
        WHERE  team_code = "{team_code}"
        """.format(team_code=team_code)

        cur = con.execute(sql)
        team_id = cur.fetchone()[0]

        sql = """
        INSERT INTO tournaments_teams (tournament_id, team_id)
        VALUES ({tournament_id}, {team_id})
        """.format(tournament_id=tournament_id, team_id=team_id)

        con.execute(sql)
        con.commit()

    sql = """
        INSERT INTO migrations (migration_name)
        VALUES
            ("{migration}")
    """.format(migration=migration)

    con.execute(sql)
    con.commit()

# Carga de resultados
migrations = os.listdir(os.path.join(migrPath, 'results'))
for migration in sorted(migrations):
    if not migration.endswith('.txt'):
        continue

    sql = """
        SELECT COUNT(*)
        FROM   migrations
        WHERE  migration_name = "{migration}"
    """.format(migration=migration)

    cur   = con.execute(sql)
    count = cur.fetchone()[0]

    if count > 0:
        continue

    with open(os.path.join(migrPath, 'results', migration)) as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('# Torneo'):
            section = 'tournament'
            continue
        elif line.startswith('# Resultados'):
            section = 'results'
            continue
        elif line.strip() == '':
            continue

        if section == 'tournament':
            tournament_name, tournament_season = line.strip().split(',')

            sql = """
                SELECT tournament_id
                FROM   tournaments
                WHERE
                    tournament_name = "{tournament_name}"
                AND
                    tournament_season = "{tournament_season}"
            """.format(tournament_name=tournament_name, tournament_season=tournament_season)

            cur = con.execute(sql)
            tournament_id = cur.fetchone()[0]
        elif section == 'results':
            match_team_code1, match_team_code2, match_score, match_history, match_additionals = line.strip().split(',')

            sql = """
                UPDATE matches
                    SET match_score = "{match_score}",
                        match_history = "{match_history}",
                        match_additionals = "{match_additionals}"
                    WHERE
                        match_team_code1 = "{match_team_code1}"
                    AND
                        match_team_code2 = "{match_team_code2}"
                    AND
                        tournament_id = {tournament_id}
            """.format(match_score=match_score, match_team_code1=match_team_code1,
                match_team_code2=match_team_code2, match_history=match_history,
                match_additionals=match_additionals, tournament_id=tournament_id)

            con.execute(sql)
            con.commit()

    sql = """
        INSERT INTO migrations (migration_name)
        VALUES
            ("{migration}")
    """.format(migration=migration)

    con.execute(sql)
    con.commit()


# Cierre conexión
con.close()
