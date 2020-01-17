"""trstats: user-specified commands"""

from .database import db_get_race
from .scraper import get_race
from .routines import text_playback

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
