import os
import random
import pandas as pd

currentDir = os.path.dirname(__file__)
dataPath   = os.path.abspath(os.path.join(currentDir, '..', 'data'))

def choose_random_word():
    words  = pd.read_csv(os.path.join(dataPath, 'words.csv'))
    nWords = len(words)
    n      = random.randint(0, nWords-1)
    return words.iloc[n,0]

def signin(username, password):
    if os.path.exists(os.path.join(dataPath, 'users.csv')):
        users = pd.read_csv(os.path.join(dataPath, 'users.csv'))
    else:
        users = pd.DataFrame([], columns=['username', 'password'])

    user = users[users['username'] == username]
    if len(user) == 0:
        return False
    elif user['password'] != password:
        return False

    return True


def signup(username):
    if os.path.exists(os.path.join(dataPath, 'users.csv')):
        users = pd.read_csv(os.path.join(dataPath, 'users.csv'))
    else:
        users = pd.DataFrame([], columns=['username', 'password'])

    if len(users[users['username'] == username]) > 0:
        return False

    password = choose_random_word()
    users.loc[len(users)] = [username, password]
    users.to_csv(os.path.join(dataPath, 'users.csv'), index=False)

    return password

