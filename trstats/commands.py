"""trstats: user-specified commands

This module contains functions that execute user-specified commands.
These functions are used mainly for creating custom flows based on
command-line arguments.

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

# Local application imports
from trstats.database import db_get_race
from trstats.scraper import get_race
from trstats.routines import text_playback


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
