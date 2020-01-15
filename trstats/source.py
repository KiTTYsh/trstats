#!/usr/bin/env python3
''' Some crazy stuff to get stuff from the place '''
# pylint: disable=too-many-lines

import os
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
