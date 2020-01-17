"""trstats: database schema

This module contains a definition of the database tables that will be used
with trstats' internal database.

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


TABLES = {
    'users': {
        'columns': [
            ('username', 'TEXT', True, None, True, True),
            ('avgwpm', 'REAL', False, None, False, False),
            ('favgwpm', 'REAL', False, None, False, False),
            ('bestwpm', 'INTEGER', False, None, False, False),
            ('races', 'INTEGER', False, None, False, False),
            ('percentile', 'REAL', False, None, False, False),
            ('skill', 'INTEGER', False, None, False, False),
            ('experience', 'INTEGER', False, None, False, False),
            ('signup', 'TEXT', False, None, False, False),
            ('keyboard', 'TEXT', False, None, False, False),
            ('premium', 'INTEGER', False, None, False, False),
            ('name', 'TEXT', False, None, False, False),
            ('gender', 'TEXT', False, None, False, False),
            ('location', 'TEXT', False, None, False, False),
            ('medals', 'INTEGER', False, None, False, False),
            ('dailygold', 'INTEGER', False, None, False, False),
            ('dailysilver', 'INTEGER', False, None, False, False),
            ('dailybronze', 'INTEGER', False, None, False, False),
            ('weeklygold', 'INTEGER', False, None, False, False),
            ('weeklysilver', 'INTEGER', False, None, False, False),
            ('weeklybronze', 'INTEGER', False, None, False, False),
            ('monthlygold', 'INTEGER', False, None, False, False),
            ('monthlysilver', 'INTEGER', False, None, False, False),
            ('monthlybronze', 'INTEGER', False, None, False, False),
            ('yearlygold', 'INTEGER', False, None, False, False),
            ('yearlysilver', 'INTEGER', False, None, False, False),
            ('yearlybronze', 'INTEGER', False, None, False, False),
            ('totalgold', 'INTEGER', False, None, False, False),
            ('totalsilver', 'INTEGER', False, None, False, False),
            ('totalbronze', 'INTEGER', False, None, False, False),
            ('picture', 'INTEGER', False, None, False, False),
            ('points', 'INTEGER', False, None, False, False),
            ('certwpm', 'INTEGER', False, None, False, False),
            ('gameswon', 'INTEGER', False, None, False, False),
        ],
        'indices': {
            'users_username': (['username'], False),
        }
    },
    'races': {
        'columns': {
            ('username', 'TEXT', True, None, False, False),
            ('race', 'INTEGER', True, None, False, False),
            ('date', 'INTEGER', False, None, False, False),
            ('speed', 'INTEGER', False, None, False, False),
            ('accuracy', 'REAL', False, None, False, False),
            ('rank', 'INTEGER', False, None, False, False),
            ('players', 'INTEGER', False, None, False, False),
            ('opponents', 'BLOB', False, None, False, False),
            ('text', 'INTEGER', False, None, False, False),
            ('typelog', 'BLOB', False, None, False, False),
            ('points', 'INTEGER', False, None, False, False),
        },
        'indices': {
            'races_user_race': (['username', 'race'], True),
        }
    },
    'encounters': {
        'columns': [
            ('username', 'TEXT', True, None, False, False),
            ('opponent', 'TEXT', True, None, False, False),
            ('matches', 'INTEGER', True, 0, False, False),
            ('wins', 'INTEGER', True, 0, False, False),
            ('losses', 'INTEGER', True, 0, False, False),
        ],
        'indices': {
            'encounters_unique': (['username', 'opponent'], True),
        }
    },
    'umeta': {
        'columns': [
            ('username', 'TEXT', True, None, True, True),
            ('lastencounter', 'INTEGER', True, 0, False, False),
            ('lasttypelog', 'INTEGER', True, 0, False, False),
            ('normals', 'INTEGER', True, 0, False, False),
            ('practices', 'INTEGER', True, 0, False, False),
            ('ghosts', 'INTEGER', True, 0, False, False),
        ],
        'indices': {
        }
    },
}
