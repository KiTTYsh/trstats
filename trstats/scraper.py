"""trstats: scraping functions

This module provides functions for acquiring data from TypeRacer by means of
scraping, in order to get data that is not provided by the API.

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
from datetime import datetime

# Third party imports
from requests import Session
from bs4 import BeautifulSoup


def get_profile(user, session=None):
    ''' Retrieves the profile of the user.
        Returns a dictionary of profile attributes. '''
    # pylint: disable=too-many-statements

    # Start a session if we weren't provided with one
    if not session:
        session = Session()

    # Get page and start parsing
    page = session.get(
        'https://data.typeracer.com/pit/profile?user=' + user).text
    soup = BeautifulSoup(page, 'html.parser')

    # Check if the profile wasn't found, return false
    # WHY DO YOU SEND ME A HTTP 200, TYPERACER?!??!???!
    if soup.find('h2', text='Profile Not Found'):
        return False

    # Establish a dictionary for our return data
    data = dict()

    # Get a numbers finder
    numbers = re.compile(r'\d+(?:\.\d+)?')

    # Profile Username
    data['username'] = soup.find('span', {'id': 'profileUsername'}).get_text()
    # Profile Average WPM
    data['avgwpm'] = int(numbers.findall(
        soup.find('span', {'id': 'profileWpmRounded'}).get_text())[0])
    # Full Average WPM
    data['favgwpm'] = float(numbers.findall(
        soup.find('td', text='Full Average').\
            parent.findAll('td')[1].get_text())[0])
    # Best Race
    data['bestwpm'] = int(numbers.findall(
        soup.find('td', text='Best Race').\
            parent.findAll('td')[1].get_text())[0])
    # Races Completed
    data['races'] = int(numbers.findall(
        soup.find('td', text='Races Completed').\
            parent.findAll('td')[1].get_text())[0])
    # WPM Percentile
    data['percentile'] = float(numbers.findall(
        soup.find('td', text='WPM Percentile').\
            parent.findAll('td')[1].get_text())[0])
    # Skill Level
    data['skill'] = soup.find('td', text='Skill Level').\
            parent.findAll('td')[1].get_text().strip()
    # Experience Level
    data['experience'] = int(numbers.findall(
        soup.find('td', text='Experience Level').\
            parent.findAll('td')[1].get_text())[0])
    # Signup Date
    data['signup'] = soup.find('td', text='Racing Since').\
            parent.findAll('td')[1].get_text().strip()
    # Keyboard Type
    data['keyboard'] = soup.find('td', text='Keyboard')
    if data['keyboard']:
        data['keyboard'] = data['keyboard'].\
            parent.findAll('td')[1].get_text().strip()
    # Premium
    data['premium'] = soup.find('td', text='Membership')
    if 'Premium' in data['premium'].parent.get_text():
        data['premium'] = True
    else:
        data['premium'] = False
    # Name
    data['name'] = soup.find('td', text='Name').\
            parent.findAll('td')[1].get_text().strip()
    # Gender
    data['gender'] = soup.find('td', text='Gender')
    if data['gender']:
        data['gender'] = data['gender'].\
            parent.findAll('td')[1].get_text().strip()
    # Location
    data['location'] = soup.find('td', text='Location')
    if data['location']:
        data['location'] = " ".join(data['location'].\
            parent.findAll('td')[1].get_text().split())
    # Awards
    award_section = soup.find('td', text='Awards')
    if award_section:
        award_section = award_section.parent.findAll('td')[1]
        data['medals'] = len(award_section.findAll('img'))
        data['dailygold'] = len(
            award_section.findAll(
                'img', {'title': re.compile('1st place in our daily.*')}))
        data['dailysilver'] = len(
            award_section.findAll(
                'img', {'title': re.compile('2nd place in our daily.*')}))
        data['dailybronze'] = len(
            award_section.findAll(
                'img', {'title': re.compile('3rd place in our daily.*')}))
        data['weeklygold'] = len(
            award_section.findAll(
                'img', {'title': re.compile('1st place in our weekly.*')}))
        data['weeklysilver'] = len(
            award_section.findAll(
                'img', {'title': re.compile('2nd place in our weekly.*')}))
        data['weeklybronze'] = len(
            award_section.findAll(
                'img', {'title': re.compile('3rd place in our weekly.*')}))
        data['monthlygold'] = len(
            award_section.findAll(
                'img', {'title': re.compile('1st place in our monthly.*')}))
        data['monthlysilver'] = len(
            award_section.findAll(
                'img', {'title': re.compile('2nd place in our monthly.*')}))
        data['monthlybronze'] = len(
            award_section.findAll(
                'img', {'title': re.compile('3rd place in our monthly.*')}))
        data['yearlygold'] = len(
            award_section.findAll(
                'img', {'title': re.compile('1st place in our yearly.*')}))
        data['yearlysilver'] = len(
            award_section.findAll(
                'img', {'title': re.compile('2nd place in our yearly.*')}))
        data['yearlybronze'] = len(
            award_section.findAll(
                'img', {'title': re.compile('3rd place in our yearly.*')}))
        data['totalgold'] = data['dailygold'] + data['weeklygold'] +\
                            data['monthlygold'] + data['yearlygold']
        data['totalsilver'] = data['dailysilver'] + data['weeklysilver'] +\
                            data['monthlysilver'] + data['yearlysilver']
        data['totalbronze'] = data['dailybronze'] + data['weeklybronze'] +\
                            data['monthlybronze'] + data['yearlybronze']
    else:
        data['medals'] = 0
        data['dailygold'] = 0
        data['dailysilver'] = 0
        data['dailybronze'] = 0
        data['weeklygold'] = 0
        data['weeklysilver'] = 0
        data['weeklybronze'] = 0
        data['monthlygold'] = 0
        data['monthlysilver'] = 0
        data['monthlybronze'] = 0
        data['yearlygold'] = 0
        data['yearlysilver'] = 0
        data['yearlybronze'] = 0
        data['totalgold'] = 0
        data['totalsilver'] = 0
        data['totalbronze'] = 0

    # Continue collecting data from API
    api = session.get('https://data.typeracer.com/users?id=tr:' + user +
                      '&universe=play').json()
    data['picture'] = api['hasPic']
    data['points'] = int(api['tstats']['points'])
    data['certwpm'] = int(api['tstats']['certWpm'])
    data['gameswon'] = int(api['tstats']['gamesWon'])

    # We're all done, send the data back!
    return data


def get_race(user, race_id, session=None):
    ''' Retrieve data on opponents from a specific race. '''

    # Start a session if we weren't provided with one
    if not session:
        session = Session()

    # Get page and start parsing
    page = session.get(
        'https://data.typeracer.com/pit/result?id=|tr:'+user+'|'+str(race_id)).\
            text
    soup = BeautifulSoup(page, 'html.parser')

    # Create dictionary for data storage
    data = dict()

    # Get a numbers finder
    numbers = re.compile(r'\d+(?:\.\d+)?')

    # Get Race Details
    race_details = soup.find('table', {'class': 'raceDetails'})
    # Username
    data['username'] = re.sub(r'.*=', '', race_details.\
        find('a', {'class': 'userProfileTextLink'}).get('href'))
    # Race Number
    data['race'] = int(numbers.findall(
        race_details.find('td', text='Race Number').\
            parent.findAll('td')[1].get_text())[0])
    # Date
    data['date'] = race_details.find('td', text='Date').\
        parent.findAll('td')[1].get_text().strip()
    data['date'] = datetime.strptime(data['date'], '%a, %d %b %Y %H:%M:%S %z')
    # Speed
    data['speed'] = int(numbers.findall(
        race_details.find('td', text='Speed').\
            parent.findAll('td')[1].get_text())[0])
    # Accuracy
    data['accuracy'] = float(numbers.findall(
        race_details.find('td', text='Accuracy').\
            parent.findAll('td')[1].get_text())[0])
    # Rank / Players
    data['rank'] = numbers.findall(
        race_details.find('td', text='Rank').\
            parent.findAll('td')[1].get_text().strip())
    data['players'] = int(data['rank'][1])
    data['rank'] = int(data['rank'][0])
    # Opponents
    opponents = race_details.find('td', text='Opponents')
    if opponents:
        data['opponents'] = list()
        opponents = opponents.parent.findAll('td')[1].findAll('a')
        for opponent in opponents:
            data['opponents'].append({
                'username': opponent.get_text(),
                'race': int(numbers.findall(opponent.get('href'))[0]),
                'rank': int(numbers.findall(opponent.next_sibling)[0])
            })
    else:
        data['opponents'] = None
    # Text ID
    data['text'] = int(numbers.findall(
        soup.find('a', text='see stats').get('href'))[0])
    # Typing Log
    data['typelog'] = soup.find('script', text=re.compile('var typingLog = '))
    if data['typelog']:
        data['typelog'] = data['typelog'].get_text().strip()
        data['typelog'] = '"'.join(data['typelog'].split('"')[1:-1])
    else:
        data['typelog'] = None

    # We have gathered all data, send it back to the caller!
    return data
