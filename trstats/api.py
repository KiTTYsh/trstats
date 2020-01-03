""" Functions for getting data from TypeRacer API """
from requests import Session

def get_player(user, session=False):
    """ Get profile data on a single user """
    if not session:
        session = Session()
    return session.get(
        'https://data.typeracer.com/users?id=tr:' + user + '&universe=play'
    ).json()
