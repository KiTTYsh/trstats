#!/usr/bin/env python3
''' Some crazy stuff to get stuff from the place '''
# pylint: disable=too-many-lines

import os
import re
import sqlite3
import json
from argparse import ArgumentParser
from datetime import datetime
from time import sleep
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


def create_database():
    ''' Instantiate the database if it doesn't exist, return the database
        if it does '''
    # Create the database connection
    dbh = sqlite3.connect('typeracer.db')
    # Create the cursor for interacting with the database
    dbc = dbh.cursor()
    # Look up all of the current tables in the database
    tables = dbc.execute(
        'SELECT name '
        'FROM sqlite_master '
        'WHERE type="table" '
        'AND name NOT LIKE "sqlite_%";').fetchall()
    # Subset the tables if we get a result
    if tables:
        tables = [row[0] for row in tables]
    # Create the users table
    if 'users' not in tables:
        print('DB: Creating \'users\' table')
        dbc.execute(
            'CREATE TABLE "users" ( '
            '  "id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, '
            '  "username" TEXT UNIQUE, '
            '  "avgwpm" INTEGER, '
            '  "favgwpm" REAL, '
            '  "bestwpm" INTEGER, '
            '  "races" INTEGER, '
            '  "percentile" REAL, '
            '  "skill" INTEGER, '
            '  "experience" INTEGER, '
            '  "signup" TEXT, '
            '  "keyboard" TEXT, '
            '  "premium" INTEGER, '
            '  "name" TEXT, '
            '  "gender" TEXT, '
            '  "location" TEXT, '
            '  "medals" INTEGER, '
            '  "dailygold" INTEGER, '
            '  "dailysilver" INTEGER, '
            '  "dailybronze" INTEGER, '
            '  "weeklygold" INTEGER, '
            '  "weeklysilver" INTEGER, '
            '  "weeklybronze" INTEGER, '
            '  "monthlygold" INTEGER, '
            '  "monthlysilver" INTEGER, '
            '  "monthlybronze" INTEGER, '
            '  "yearlygold" INTEGER, '
            '  "yearlysilver" INTEGER, '
            '  "yearlybronze" INTEGER, '
            '  "totalgold" INTEGER, '
            '  "totalsilver" INTEGER, '
            '  "totalbronze" INTEGER, '
            '  "picture" INTEGER, '
            '  "points" INTEGER, '
            '  "certwpm" INTEGER, '
            '  "gameswon" INTEGER '
            ');'
        )
        dbc.execute('CREATE INDEX "users_username" ON "users" ("username");')
        dbh.commit()
    # Create the races table
    if 'races' not in tables:
        print('DB: Creating \'races\' table')
        dbc.execute(
            'CREATE TABLE "races" ( '
            '  "id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, '
            '  "username" TEXT, '
            '  "race" INTEGER, '
            '  "date" INTEGER, '
            '  "speed" INTEGER, '
            '  "accuracy" REAL, '
            '  "rank" INTEGER, '
            '  "players" INTEGER, '
            '  "opponents" BLOB, '
            '  "text" INTEGER, '
            '  "typelog" BLOB, '
            '  "points" INTEGER '
            ');'
        )
        dbc.execute(
            'CREATE UNIQUE INDEX "races_user_race" ON "races" ( '
            '  "username", '
            '  "race" '
            ');'
        )
        dbh.commit()
    # Create the encounters table
    if 'encounters' not in tables:
        print('DB: Creating \'encounters\' table')
        dbc.execute(
            'CREATE TABLE "encounters" ( '
            '  "id" INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, '
            '  "username" TEXT, '
            '  "opponent" TEXT, '
            '  "matches" INTEGER, '
            '  "wins" INTEGER, '
            '  "losses" INTEGER '
            ');'
        )
        dbc.execute(
            'CREATE UNIQUE INDEX "encounters_unique" ON "encounters" '
            '("username", "opponent");'
        )
        dbh.commit()
    # Create the user meta table
    if 'umeta' not in tables:
        print('DB: Creating \'umeta\' table')
        dbc.execute(
            'CREATE TABLE "umeta" ( '
            '  "username" TEXT NOT NULL UNIQUE, '
            '  "lastencounter" INTEGER DEFAULT 0, '
            '  "lasttypelog" INTEGER DEFAULT 0, '
            '  "normals" INTEGER DEFAULT 0, '
            '  "practices" INTEGER DEFAULT 0, '
            '  "ghosts" INTEGER DEFAULT 0, '
            '  PRIMARY KEY("username") '
            ');'
        )
        dbh.commit()
    return dbh


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


def generate_output(user, dbh):
    """ Generate nice HTML output for easy viewing of data! :D """
    # pylint: disable=line-too-long
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    dbc = dbh.cursor()
    html = \
f'''<!DOCTYPE html>
<html>
  <head>
    <link rel="shortcut icon" href="https://data.typeracer.com/favicon.ico" type="image/vnd.microsoft.icon">
    <title>TRStats {user['username']}</title>
    <link rel="stylesheet" type="text/css" href="https://data.typeracer.com/public/theme/theme.css" media="screen">
    <style type="text/css">''' '''
      .title { width: 180px; }
      table td:first-child {font-weight:bold;}
      table.scoresTable td:first-child {font-weight:normal;}
      .awardsTable {border-collapse: collapse;}
      .awardsTable th, .awardsTable td {border: 1px dotted; padding-right: 5px;}
      .awardsTable td {text-align: center;}

      table.scoresTable {width:100%;margin-top:10px;}
      table.scoresTable td, table.scoresTable th {vertical-align:middle;text-align:center;padding-right:5px;padding-left:5px;border-left:1px dotted gray;}
      table.scoresTable th {border-bottom:1px dotted gray;border-top:1px dotted gray;}
      table.scoresTable td:first-child, table.scoresTable th:first-child {border-left: none;}
      table.scoresTable tr:first-child {background-color:aliceblue;}
      h3 {font-size:1.2em;font-family:Arial, Helvetica, sans-serif;margin:10px 0px 18px 0px;border-bottom: 1px solid #bbb;}
    </style>''' f'''
  </head>
  <body>
    <div class="container">
      <table cellpadding="0" cellspacing="0" class="themeHeader" width="100%"><tr>
        <td class="title" valign="top">
          <h1>not typeracer</h1>
          <div class="subTitle" style="font-weight:bold;color:#fff;text-align:right;">Stats for {user['username']}</div>
        </td>
        <td class="navigation"><div style="margin-bottom: 10px;">
          <a href="#latest">Latest</a>
          <a href="#encounters">Encounters</a>
          <a href="#fastest">Fastest</a>
        </div></td>
      </tr></table>
      <div class="main">
        <div class="themeContent" style="width: 100%">
          <table width="100%"><tr><td><h2>Racer Profile</h2></td></tr></table>
          <table width="100%" style="border-bottom: solid 1px gray;">
            <tr>
              <td nowrap>
                <span id="profileUsername" style="font-size:2em;">'''
    if user['name']:
        html += f"{user['name']} ({user['username']})"
    else:
        html += user['username']
    html += '</span>\n'
    # Annoying stuff for racer experience level
    if user['premium']:
        exptype = 'Racer'
    else:
        exptype = 'Typist'
    html += '                <img src="https://data.typeracer.com'
    html += '/public/images/insignia/'
    if user['premium']:
        html += 'r'
    else:
        html += 't'
    html += \
f'''{str(user['experience'])}.png" alt="{exptype} {str(user['experience'])} Insignia" title="{exptype} {str(user['experience'])} Insignia">
              </td>
              <td nowrap align="right">
                <span id="profileWpmRounded" style="font-size:2em; cursor:help;" title='Average of the last 10 races'>
                  {str(user['avgwpm'])} WPM
                </span>
              </td>
            </tr>
          </table>
          <table width="100%" cellsppacing="5">
            <tr>
              <td width="300" style="font-weight:normal; vertical-align: top;">
                <div style="margin-bottom:8px;">
                  <a href="https://data.typeracer.com/pit/message_compose?to={user['username']}&fix=1" title="Send a private message to this user">Message</a> |
                  <a href="https://data.typeracer.com/pit/flag?user={user['username']}" title="Report this user for a policy violation">Report</a> |
                  <a href="https://data.typeracer.com/pit/friend_request?user={user['username']}">Send friend request</a>
                </div>
'''
    if user['picture']:
        html += \
f'''                <img src="https://data.typeracer.com/misc/pic?uid=tr:{user['username']}&size=large" alt="">
'''
    else:
        html += \
f'''                <img src="https://data.typeracer.com/public/images/silhouette300.gif" title="{user['username']}" alt="">
'''
    html += \
f'''
              </td>
              <td valign="top" align="left">
                <table class="profileInformation" width="100%" cellspacing="5">
                  <tr><td>Full Average</td><td>{str(user['favgwpm'])} WPM</td></tr>
                  <tr><td>Best Race</td><td>{str(user['bestwpm'])} WPM</td></tr>
                  <tr><td>Races Completed</td><td>{str(user['races'])}</td></tr>
                  <tr height="20"></tr>
                  <tr><td>WPM Percentile</td><td>{str(user['percentile'])}%</td></tr>
                  <tr><td>Skill Level</td><td>{user['skill']}</td></tr>
                  <tr><td>Experience Level</td><td>{exptype} {str(user['experience'])}</td></tr>
                  <tr height="20"></tr>
                  <tr><td>Racing Since</td><td>{str(user['signup'])}</td></tr>
'''
    if user['keyboard']:
        html += '                  <tr><td><b>Keyboard</b></td>'
        html += '<td>' + str(user['keyboard']) + '</td></tr>\n'
    html += \
f'''                  <tr><td>Membership</td><td>{'Premium' if user['premium'] else 'Basic'}</td></tr>
                  <tr height="20"></tr>
'''
    if user['name']:
        html += '                  <tr><td><b>Name</b></td>'
        html += '<td>' + user['name'] + '</td></tr>\n'
    if user['gender']:
        html += '                  <tr><td><b>Gender</b></td>'
        html += '<td>' + user['gender'] + '</td></tr>\n'
    if user['location']:
        html += '                  <tr><td><b>Location</b></td>'
        html += '<td>' + user['location'] + '</td></tr>\n'
    if user['medals']:
        html += '                  <tr><td><b>Awards</b></td>'
        html += '<td>' + str(user['medals']) + '</td></tr>\n'
    html += \
f'''                </table>
              </td>
            </tr>
          </table>
'''
    if user['medals']:
        html += \
f'''          <table class="scoresTable">
            <tr><th>Medal</th><th>Daily</th><th>Weekly</th><th>Monthly</th><th>Yearly</th><th>Total</th></tr>
            <tr><td><img src="https://data.typeracer.com/public/images/medals/32px/1.cache.png"></td><td>{str(user['dailygold'])}</td><td>{str(user['weeklygold'])}</td><td>{str(user['monthlygold'])}</td><td>{str(user['yearlygold'])}</td><td>{str(user['totalgold'])}</td></tr>
            <tr><td><img src="https://data.typeracer.com/public/images/medals/32px/2.cache.png"></td><td>{str(user['dailysilver'])}</td><td>{str(user['weeklysilver'])}</td><td>{str(user['monthlysilver'])}</td><td>{str(user['yearlysilver'])}</td><td>{str(user['totalsilver'])}</td></tr>
            <tr><td><img src="https://data.typeracer.com/public/images/medals/32px/3.cache.png"></td><td>{str(user['dailybronze'])}</td><td>{str(user['weeklybronze'])}</td><td>{str(user['monthlybronze'])}</td><td>{str(user['yearlybronze'])}</td><td>{str(user['totalbronze'])}</td></tr>
          </table>
'''
    html += \
f'''          <h3 id="latest">Latest Race Results</h3>
          <table class="scoresTable">
            <tr><th>Race #</th><th>Speed</th><th>Accuracy</th><th>Points</th><th>Place</th><th>Date</th><th>Options</th></tr>
'''
    dbr = dbc.execute(
        'SELECT race, speed, accuracy, rank, players, date FROM races '
        'WHERE username=? ORDER BY race DESC LIMIT 50',
        [user['username']]
    ).fetchall()
    if dbr:
        for race in dbr:
            html += '            <tr>'
            html += '<td><a href="https://data.typeracer.com/pit/result?id=|tr'\
                    f':{user["username"]}|{str(race[0])}" '\
                    f'title="Click to see the details">{str(race[0])}</td>'
            html += f'<td>{str(race[1])}</td>'
            html += f'<td>{str(race[2])}</td>'
            html += '<td>Error</td>'
            html += f'<td>{str(race[3])}/{str(race[4])}</td>'
            html += f'<td>{"".join(race[5][:-6])}</td>'

            html += '<td><a href="https://data.typeracer.com/pit/result?id=|tr'\
                    f':{user["username"]}|{str(race[0])}" '\
                    'title="Click to see the replay">'\
                    '<img src="https://data.typeracer.com/public/images/'\
                    'movie24.cache.png"></a>'\
                    '<a href="https://play.typeracer.com/?ghost=%7Ctr:'\
                    f'{user["username"]}%7C{str(race[0])}" '\
                    'title="Redo in ghost racing mode">'\
                    '<img src="https://data.typeracer.com/public/images/'\
                    'ghost24.cache.png"></a></td>\n'
    html += \
f'''          </table>
          <h3 id="encounters">Encounters</h3>
          <table class="scoresTable">
            <tr><th>Username</th><th>Matches</th><th>Wins</th><th>Losses</th><th>Win %</th></tr>
'''
    dbr = dbc.execute(
        'SELECT opponent, matches, wins, losses FROM encounters '
        'WHERE username=? ORDER BY matches DESC LIMIT 50',
        [user['username']]
    ).fetchall()
    if dbr:
        for match in dbr:
            html += '            <tr>'
            html += '<td style="text-align:left;">'\
                    '<img src="https://data.typeracer.com/misc/pic?uid=tr:'\
                    f'{match[0]}&size=thumb" height=24px> {match[0]}</td>'
            html += f'<td>{str(match[1])}</td>'
            html += f'<td>{str(match[2])}</td>'
            html += f'<td>{str(match[3])}</td>'
            matchpercent = round(match[2]/(match[2]+match[3])*100, 1)
            html += f'<td align="right">{str(matchpercent)}</td></tr>\n'
    html += \
'''          </table>
          <h3 id="fastest">Fastest Races</h3>
          <table class="scoresTable">
            <tr><th>Race #</th><th>Speed</th><th>Accuracy</th><th>Points</th><th>Place</th><th>Date</th><th>Options</th></tr>
'''
    dbr = dbc.execute(
        'SELECT race, speed, accuracy, rank, players, date FROM races '
        'WHERE username=? ORDER BY speed DESC LIMIT 50',
        [user['username']]
    ).fetchall()
    if dbr:
        for race in dbr:
            html += '            <tr>'
            html += '<td><a href="https://data.typeracer.com/pit/result?id=|tr'\
                    f':{user["username"]}|{str(race[0])}" '\
                    f'title="Click to see the details">{str(race[0])}</td>'
            html += f'<td>{str(race[1])}</td>'
            html += f'<td>{str(race[2])}</td>'
            html += '<td>Error</td>'
            html += f'<td>{str(race[3])}/{str(race[4])}</td>'
            html += f'<td>{"".join(race[5][:-6])}</td>'

            html += '<td><a href="https://data.typeracer.com/pit/result?id=|tr'\
                    f':{user["username"]}|{str(race[0])}" '\
                    'title="Click to see the replay">'\
                    '<img src="https://data.typeracer.com/public/images/'\
                    'movie24.cache.png"></a>'\
                    '<a href="https://play.typeracer.com/?ghost=%7Ctr:'\
                    f'{user["username"]}%7C{str(race[0])}" '\
                    'title="Redo in ghost racing mode">'\
                    '<img src="https://data.typeracer.com/public/images/'\
                    'ghost24.cache.png"></a></td>\n'
    html += \
'''        </table>
        </div>
      </div>
    </div>
    <div class="footer">
      This site is not TypeRacer, and has no affiliation.
      <a target="_blank" href="http://play.typeracer.com/">This is TypeRacer.</a>
      <div class="clearer">&nbsp;</div>
    </div>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
    <script type="text/javascript">
      $('th').click(function(){
        var table = $(this).parents('table').eq(0)
        var rows = table.find('tr:gt(0)').toArray().sort(comparer($(this).index()))
        this.asc = !this.asc
        if (!this.asc){rows = rows.reverse()}
        for (var i = 0; i < rows.length; i++){table.append(rows[i])}
      })
      function comparer(index) {
        return function(a, b) {
          var valA = getCellValue(a, index), valB = getCellValue(b, index)
          return $.isNumeric(valA) && $.isNumeric(valB) ? valA - valB : valA.toString().localeCompare(valB)
        }
      }
      function getCellValue(row, index){ return $(row).children('td').eq(index).text() }
    </script>
  </body>
</html>
'''
    if not os.path.isdir('output'):
        try:
            os.mkdir('output')
        except FileExistsError:
            print('Could not create output directory!')
            return

    file = open('output/' + user['username'] + '.html', 'wb')
    file.write(html.encode('utf-8'))
    file.close()


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
    dbh = create_database()
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
        cmd_playback(user, args.playback, dbh)
        return
    if args.wipe_encounters:
        cmd_wipe_encounters(user, dbh)
        return

    # Assume no functional arguments have been specified, continue normally...
    # update the user in the database, since we grabbed it already
    db_put_user(user, dbh)
    # Download all races currently known for the user
    if args.races:
        download_races(user, dbh, session)
    if args.encounters:
        calculate_encounters(user, dbh)
    if args.output:
        generate_output(user, dbh)


if __name__ == "__main__":
    main()
