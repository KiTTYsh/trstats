"""trstats: application entry point

This is the script that handles running trstats as an application,
including interpreting command-line input.

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
from argparse import ArgumentParser

# Third party imports
from requests import Session

# Local application imports
from trstats.database import Database, db_put_user
from trstats.commands import cmd_playback, cmd_wipe_encounters
from trstats.routines import calculate_encounters, download_races
from trstats.scraper import get_profile
from trstats.output import generate_output


def main():
    ''' The main function for this program. '''

    # Check for specified command-line options
    parser = ArgumentParser(
        description='Retrieves a variety of statistics from TypeRacer, '
                    'and compiles it into an HTML file for further '
                    'analysis :)')
    parser.add_argument(
        'username', nargs='?',
        help='The username of the TypeRacer user that you want data for')
    parser.add_argument(
        '-f', '--fast', action='store_true',
        help='Use API instead of scraping where possible'
    )
    parser.add_argument(
        '--no-races', dest='races', action='store_false',
        help='skip downloading race data'
    )
    parser.add_argument(
        '--no-encounters', dest='encounters', action='store_false',
        help='skip processing encounters'
    )
    parser.add_argument(
        '--no-output', dest='output', action='store_false',
        help='skip creating output for the user'
    )
    fnargs = parser.add_argument_group(
        'functional arguments',
        'Use these to perform a single function').\
        add_mutually_exclusive_group()
    fnargs.add_argument(
        '-p', '--playback', metavar='raceid', action='store', type=int,
        help='Play back a race on the console')
    dangerargs = parser.add_argument_group(
        'dangerous arguments',
        'Using these arguments can seriously damage your database!'
    )
    dangerargs.add_argument(
        '-R', '--download-race', metavar='raceid',
        help='Manually download or update a race record'
    )
    dangerargs.add_argument(
        '--wipe-encounters', action='store_true',
        help='Remove all encounter records for a user'
    )
    args = parser.parse_args()

    # Get our database and HTTP sessions
    database = Database('typeracer.db')
    session = Session()

    # Get the user that we want to do things for
    if args.username:
        target = args.username
    else:
        target = input('Target player: ')

    # Download profile data for the target user, and ensure they exist
    user = get_profile(target, session)
    if not user:
        print('User not found!')
        return

    # Check for functional arguments
    if args.playback:
        cmd_playback(user, args.playback, database.dbh)
        return
    if args.wipe_encounters:
        cmd_wipe_encounters(user, database.dbh)
        return

    # Assume no functional arguments have been specified, continue normally...
    # update the user in the database, since we grabbed it already
    db_put_user(user, database.dbh)
    # Download all races currently known for the user
    if args.races:
        download_races(user, database.dbh, session)
    if args.encounters:
        calculate_encounters(user, database.dbh)
    if args.output:
        generate_output(user, database.dbh)


if __name__ == "__main__":
    main()
