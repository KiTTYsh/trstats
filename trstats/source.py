#!/usr/bin/env python3
''' Some crazy stuff to get stuff from the place '''

import re
import json
from datetime import datetime
from time import sleep
from .scraper import get_race


def db_put_user(user, dbh):
    ''' Insert or update a user in the database '''
    dbc = dbh.cursor()
    dbq = (
        user['username'], user['avgwpm'], user['favgwpm'], user['bestwpm'],
        user['races'], user['percentile'], user['skill'], user['experience'],
        user['signup'], user['keyboard'], user['premium'], user['name'],
        user['gender'], user['location'], user['medals'], user['dailygold'],
        user['dailysilver'], user['dailybronze'], user['weeklygold'],
        user['weeklysilver'], user['weeklybronze'], user['monthlygold'],
        user['monthlysilver'], user['monthlybronze'], user['yearlygold'],
        user['yearlysilver'], user['yearlybronze'], user['totalgold'],
        user['totalsilver'], user['totalbronze'], user['picture'],
        user['points'], user['certwpm'], user['gameswon']
    )
    dbc.execute(
        'INSERT OR REPLACE INTO users ( '
        '  username, avgwpm, favgwpm, bestwpm, races, percentile, skill, '
        '  experience, signup, keyboard, premium, name, gender, location, '
        '  medals, dailygold, dailysilver, dailybronze, weeklygold, '
        '  weeklysilver, weeklybronze, monthlygold, monthlysilver, '
        '  monthlybronze, yearlygold, yearlysilver, yearlybronze, totalgold, '
        '  totalsilver, totalbronze, picture, points, certwpm, gameswon ) '
        'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'
        '?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);',
        dbq
    )
    dbh.commit()


def db_get_user(username, dbh):
    ''' Retrieve a user from the database '''
    dbc = dbh.cursor()
    dbr = dbc.execute('SELECT '
                      '  username, '   # 0
                      '  avgwpm, '     # 1
                      '  favgwpm, '    # 2
                      '  bestwpm, '    # 3
                      '  races, '      # 4
                      '  percentile, ' # 5
                      '  skill, '      # 6
                      '  experience, ' # 7
                      '  signup '      # 8
                      'FROM users WHERE username=?',
                      [username]).fetchall()
    if dbr:
        data = dict()
        data['username'] = dbr[0][0]
        data['avgwpm'] = dbr[0][1]
        data['favgwpm'] = dbr[0][2]
        data['bestwpm'] = dbr[0][3]
        data['races'] = dbr[0][4]
        data['percentile'] = dbr[0][5]
        data['skill'] = dbr[0][6]
        data['experience'] = json.loads(dbr[0][7])
        data['signup'] = dbr[0][8]
        return data
    return False


def db_put_race(race, dbh):
    ''' Insert or update a race in the database '''
    dbc = dbh.cursor()
    dbq = (
        race['username'], race['race'], race['date'], race['speed'],
        race['accuracy'], race['rank'], race['players'],
        json.dumps(race['opponents']), race['text'], race['typelog']
    )
    dbc.execute(
        'INSERT OR REPLACE INTO races ( '
        '  username, race, date, speed, accuracy, rank, players, opponents, '
        '  text, typelog ) '
        'VALUES (?,?,?,?,?,?,?,?,?,?);',
        dbq
    )
    # dbh.commit()


def db_get_race(user, raceid, dbh):
    """Fetch a race from the database.

    Arguments:
        user {dictionary} -- The user profile to retrieve a race for
        raceid {integer} -- The ID of the race to retrieve
        dbh {sqlite3.Connection} - The connection to the database

    Returns:
        dictionary -- Details for the requested race
    """
    dbc = dbh.cursor()
    dbr = dbc.execute('SELECT '
                      '  username, '  # 0
                      '  race, '      # 1
                      '  date, '      # 2
                      '  speed, '     # 3
                      '  accuracy, '  # 4
                      '  rank, '      # 5
                      '  players, '   # 6
                      '  opponents, ' # 7
                      '  text, '      # 8
                      '  typelog '    # 9
                      'FROM races '
                      'WHERE username=? AND race=?',
                      [user['username'], raceid]).fetchall()
    if dbr:
        data = dict()
        data['username'] = dbr[0][0]
        data['race'] = dbr[0][1]
        data['date'] = datetime.strptime(dbr[0][2], '%Y-%m-%d %H:%M:%S%z')
        data['speed'] = dbr[0][3]
        data['accuracy'] = dbr[0][4]
        data['rank'] = dbr[0][5]
        data['players'] = dbr[0][6]
        data['opponents'] = json.loads(dbr[0][7])
        data['text'] = dbr[0][8]
        data['typelog'] = dbr[0][9]
        return data
    return False


def time_remaining(current, total, currenttime):
    ''' Give a user-acceptable time estimate '''
    ratio = currenttime / current
    done_time = int((total-current) * ratio)
    rhour, rmin = divmod(done_time, 3600)
    rmin, rsec = divmod(rmin, 60)
    return str(rhour).zfill(2) + ':' + str(rmin).zfill(2) +\
           ':' + str(rsec).zfill(2)


def download_races(user, dbh, session):
    ''' Download all races for a user '''
    # pylint: disable=too-many-locals

    # Get a database cursor
    dbc = dbh.cursor()

    # Check the last downloaded race for a user
    dbr = dbc.execute(
        'SELECT race FROM races '
        'WHERE username=? ORDER BY race DESC LIMIT 1;',
        [user['username']]
    ).fetchall()
    if dbr:
        lastrace = dbr[0][0]
    else:
        lastrace = 0
    print('Last race was ' + str(lastrace))

    # Start downloading these things like hotcakes!
    current_download = 0
    total_download = user['races'] - lastrace
    start_time = datetime.now()
    commit_counter = 0
    for raceid in range(lastrace+1, user['races']+1):
        # increment download counter
        current_download += 1
        commit_counter += 1
        # time estimation
        done_str = time_remaining(current_download, total_download,
                                  (datetime.now()-start_time).total_seconds())

        # Status output
        print('Fetching race ' + str(raceid) + '/' + str(user['races']) + ' (' +
              str(current_download) + '/' + str(total_download) + ') for ' +
              user["username"] + ' [' + done_str + ']', end='\033[K\r')

        # Actual race download
        race = get_race(user['username'], raceid, session)
        db_put_race(race, dbh)

        # Commit to database?
        if commit_counter >= 20:
            dbh.commit()
            commit_counter = 0

    # Final database commit
    dbh.commit()

    print('\nDownloads for ' + user['username'] + ' complete!')


def calculate_encounters(user, dbh):
    ''' Calculates wins and losses from one user to opponents '''
    # pylint: disable=too-many-branches

    # Get the database cursor
    dbc = dbh.cursor()

    # Ensure the user's umeta row exists
    dbc.execute('INSERT OR IGNORE INTO umeta (username) VALUES (?)',
                [user['username']])
    dbh.commit()

    # Get last downloaded race
    dbr = dbc.execute(
        'SELECT race FROM races '
        'WHERE username=? ORDER BY race DESC LIMIT 1;',
        [user['username']]
    ).fetchall()
    if dbr:
        lastrace = dbr[0][0]
    else:
        return
    # Get last processed race
    dbr = dbc.execute(
        'SELECT lastencounter FROM umeta WHERE username=?', [user['username']]
    ).fetchall()
    if dbr:
        if dbr[0][0]:
            lastprocessed = dbr[0][0]
        else:
            lastprocessed = 0
    else:
        return

    # Get all races for user
    commit_counter = 0
    start_time = datetime.now()
    for raceid in range(lastprocessed+1, lastrace+1):
        commit_counter += 1
        race = db_get_race(user, raceid, dbh)
        done_str = time_remaining(raceid-lastprocessed, lastrace,
                                  (datetime.now()-start_time).total_seconds())
        print('Calculating encounters ' + str(raceid) + '/' + str(lastrace) +
              ' [' + done_str + ']', end='\r')
        if race['opponents']:
            dbc.execute('UPDATE umeta SET normals=normals+1 WHERE username=?',
                        [user['username']])
            for opponent in race['opponents']:
                if race['rank'] < opponent['rank']:
                    dbc.execute(
                        'INSERT INTO encounters '
                        '  (username, opponent, matches, wins, losses) '
                        'VALUES (?, ?, 1, 1, 0) '
                        'ON CONFLICT(username, opponent) '
                        'DO UPDATE SET wins=wins+1, matches=matches+1;',
                        [user['username'], opponent['username']])
                else:
                    dbc.execute(
                        'INSERT INTO encounters '
                        '  (username, opponent, matches, wins, losses) '
                        'VALUES (?, ?, 1, 0, 1) '
                        'ON CONFLICT(username, opponent) '
                        'DO UPDATE SET losses=losses+1, matches=matches+1;',
                        [user['username'], opponent['username']])
        else:
            if race['players'] == 1:
                dbc.execute(
                    'UPDATE umeta SET practices=practices+1 WHERE username=?',
                    [user['username']])
            elif race['players'] == 2:
                dbc.execute(
                    'UPDATE umeta SET ghosts=ghosts+1 WHERE username=?',
                    [user['username']])
            else:
                dbc.execute(
                    'UPDATE umeta SET normals=normals+1 WHERE username=?',
                    [user['username']])

        dbc.execute('UPDATE umeta SET lastencounter=? WHERE username=?',
                    [raceid, user["username"]])
        if commit_counter >= 10:
            dbh.commit()
            commit_counter = 0
    dbh.commit()
    print('\nDone calculating encounters!')


def text_playback(text):
    """ Attempts to accurately play back a typelog on the console """
    num = re.compile('^[0-9]$')
    output = False
    timestr = ''
    for character in list(text.split('|')[1]):
        if output:
            sleep(float(timestr)/1000)
            timestr = ''
            print(character, end='', flush=True)
            output = False
        else:
            if character == '+':
                output = True
            elif character == '-':
                print('\b', end='', flush=True)
            elif num.match(character):
                timestr += character
            elif character == ',':
                if timestr:
                    sleep(float(timestr)/1000)
                    timestr = ''
    print('')


def cmd_playback(user, raceid, dbh):
    """ Handles the playback argument on commandline """
    # Check that the race is feasible to exist
    if raceid > user['races']:
        print(f'ERROR: {user["username"]} has only played '
              f'{user["races"]} races!')
        return
    # Grab the race from the database
    race = db_get_race(user, raceid, dbh)
    # Attempt to grab the race from the internet if it's not locally available
    if not race:
        print('Downloading race ' + str(raceid) + ' for ' + user['username'])
        race = get_race(user['username'], raceid)
    # If we have no local typelog, download online anyway
    elif not race['typelog']:
        print('No typelog in database, checking online!')
        race = get_race(user['username'], raceid)
    # If we still don't have a typelog, give up!
    if not race['typelog']:
        print('Couldn\'t find a typelog for that race!')
        return
    print(f'] {user["username"]} Race:{str(race["race"])} '
          f'WPM:{str(race["speed"])} Accuracy:{str(race["accuracy"])}')
    text_playback(race['typelog'])


def cmd_wipe_encounters(user, dbh):
    ''' Wipe all encounters for the specified user '''
    dbc = dbh.cursor()
    dbc.execute('DELETE FROM encounters WHERE username=?', [user['username']])
    dbc.execute('UPDATE umeta SET lastencounter=0 WHERE username=?',
                [user['username']])
    dbh.commit()
    print('Removed all encounter records for ' + user['username'] + '!')
