""" Generate nice statistics pages for viewing """
import os

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
