"""trstats: typeracer API data acquisition functions

Functions that use the typeracer official API to acquire data.

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

# Third party imports
from requests import Session


def get_player(user, session=False):
    """ Get profile data on a single user """
    if not session:
        session = Session()
    return session.get(
        'https://data.typeracer.com/users?id=tr:' + user + '&universe=play'
    ).json()
