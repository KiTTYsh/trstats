"""trstats: common program routines

This module contains all internally-used routines.

This file is part of trstats.

trstats is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

trstats is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with trstats.  If not, see <https://www.gnu.org/licenses/>.
"""

# Standard library imports
import re
from time import sleep
from datetime import datetime

# Local application imports
from trstats.database import db_get_race, db_put_race
from trstats.scraper import get_race


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
