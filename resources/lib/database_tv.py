#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import re
from datetime import date, datetime
from bs4 import BeautifulSoup
from sqlite3 import dbapi2 as sqlite

import simplejson as json

import xbmcgui
import common
import connection
import database_common as db_common


def create():
    c = _database.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS series
                (series_id INTEGER PRIMARY KEY,
                 title TEXT UNIQUE,
                 url TEXT,
                 year INTEGER,
                 studio TEXT,
                 network TEXT,
                 directors TEXT,
                 actors TEXT,
                 genres TEXT,
                 favor BOOLEAN DEFAULT 0,
                 last_update timestamp);''')

    c.execute('''CREATE TABLE IF NOT EXISTS season
                (season_id INTEGER PRIMARY KEY,
                 series_id INTEGER,
                 title TEXT,
                 season_no INTEGER,
                 url TEXT,
                 last_update timestamp,
                 FOREIGN KEY(series_id) REFERENCES series(series_id) ON DELETE CASCADE);''')

    c.execute('''CREATE TABLE IF NOT EXISTS episode
                (season_id INTEGER,
                 title TEXT,
                 episode_no INTEGER,
                 plot TEXT,
                 air_date timestamp,
                 play_count INTEGER DEFAULT 0,
                 PRIMARY KEY (season_id, title),
                 FOREIGN KEY(season_id) REFERENCES season(season_id) ON DELETE CASCADE);''')

    _database.commit()
    c.close()


def insert_series(title, url, directors=None, actors=None, genres=None, year=None, studio=None, network=None):
    c = _database.cursor()
    row = c.execute('SELECT series_id FROM series WHERE title = ?', (title,)).fetchone()
    if row:
        c.execute('''UPDATE series SET
          title = :title,
          url = :url,
          directors = :directors,
          actors = :actors,
          genres = :genres,
          year = :year,
          studio = :studio,
          network = :network,
          last_update = :last_update
          WHERE series_id = :series_id
          ''', {
            'series_id': row['series_id'],
            'title': title,
            'url': url,
            'directors': directors,
            'actors': actors,
            'genres': genres,
            'year': year,
            'studio': studio,
            'network': network,
            'last_update': datetime.now()
        })
    else:
        c.execute('''INSERT INTO series (
          title,
          url,
          directors,
          actors,
          genres,
          year,
          studio,
          network,
          last_update) VALUES (
            :title,
            :url,
            :directors,
            :actors,
            :genres,
            :year,
            :studio,
            :network,
            :last_update
          )''', {
            'title': title,
            'url': url,
            'directors': directors,
            'actors': actors,
            'genres': genres,
            'year': year,
            'studio': studio,
            'network': network,
            'last_update': datetime.now()
        })

    _database.commit()
    c.close()


def insert_season(series_id, title, url, season_no):
    c = _database.cursor()
    row = c.execute('SELECT season_id FROM season WHERE title = ? AND series_id = ?', (title,series_id)).fetchone()
    if row:
        c.execute('''UPDATE season SET
          title = :title,
          season_no = :season_no,
          url = :url,
          last_update = :last_update
          WHERE season_id = :season_id
          ''', {
            'season_id': row['season_id'],
            'title': title,
            'season_no': season_no,
            'url': url,
            'last_update': datetime.now()
        })
    else:
        c.execute('''INSERT INTO season (series_id, title, season_no, url, last_update) VALUES (
            :series_id,
            :title,
            :season_no,
            :url,
            :last_update
          )''', {
            'series_id': series_id,
            'title': title,
            'season_no': season_no,
            'url': url,
            'last_update': datetime.now()
        })

    _database.commit()
    c.close()


def insert_episode(season_id, title, episode_no=None, plot=None, air_date=None):
    c = _database.cursor()
    c.execute('''INSERT OR REPLACE INTO episode (season_id, title, episode_no, plot, air_date, play_count) VALUES (
        :season_id,
        :title,
        :episode_no,
        :plot,
        :air_date,
        (SELECT play_count FROM episode WHERE season_id = :season_id AND title = :title)
      )''', {
        'season_id': season_id,
        'title': title,
        'episode_no': episode_no,
        'plot': plot,
        'air_date': air_date
    })
    _database.commit()
    c.close()


def lookup_series(content_id):
    c = _database.cursor()
    return c.execute('SELECT DISTINCT * FROM series WHERE series_id = (?)', (content_id,))


def lookup_season(content_id):
    c = _database.cursor()
    return c.execute('SELECT DISTINCT * FROM season WHERE season_id = (?)', (content_id,))


def lookup_episode(title, season_id):
    c = _database.cursor()
    return c.execute('SELECT DISTINCT * FROM episode WHERE title = (?) AND season_id = ?', (title,season_id))


def delete_series(content_id):
    c = _database.cursor()
    c.execute('DELETE FROM series WHERE series_id = (?)', (content_id,))
    c.close()


def watch_episode(content_id):
    # TODO make this actually increment
    c = _database.cursor()
    c.execute("UPDATE episode SET play_count = 1 WHERE episode_id = (?)", (content_id,))
    _database.commit()
    c.close()
    return c.rowcount


def unwatch_episode(content_id):
    c = _database.cursor()
    c.execute("UPDATE episode SET play_count=? WHERE episode_id = (?)", (0, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def favor_series(content_id):
    c = _database.cursor()
    c.execute("UPDATE series SET favor=? WHERE series_id=?", (True, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def unfavor_series(content_id):
    c = _database.cursor()
    c.execute("UPDATE series SET favor=? WHERE series_id=?", (False, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def get_series(genrefilter=False, yearfilter=False, directorfilter=False, watchedfilter=False, favorfilter=False,
               actorfilter=False, alphafilter=False, studiofilter=False):
    c = _database.cursor()
    if genrefilter:
        genrefilter = '%' + genrefilter + '%'
        return c.execute('SELECT DISTINCT * FROM series WHERE genres LIKE (?)',
                         (genrefilter,))
    elif actorfilter:
        actorfilter = '%' + actorfilter + '%'
        return c.execute('SELECT DISTINCT * FROM series WHERE actors LIKE (?)',
                         (actorfilter,))
    elif directorfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE directors LIKE (?)',
                         (directorfilter,))
    elif studiofilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE studio = (?)', (studiofilter,))
    elif yearfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE year = (?)', (int(yearfilter),))
    elif watchedfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE playcount > 0')
    elif favorfilter:
        return c.execute('SELECT DISTINCT * FROM series WHERE favor = 1')
    elif alphafilter:
        if alphafilter == '#':
            return c.execute("SELECT DISTINCT * FROM series WHERE title REGEXP '^[^A-Za-z]{1}'")
        else:
            return c.execute('SELECT DISTINCT * FROM series WHERE title LIKE ?',
                         (alphafilter + '%',))
    else:
        return c.execute('SELECT DISTINCT * FROM series')


def get_series_season_count(series_id):
    c = _database.cursor()
    row = c.execute('''SELECT COUNT(sea.season_id) AS total_seasons
          FROM season AS sea
          JOIN series AS ser ON ser.series_id = sea.series_id
          WHERE ser.series_id = (?)
          GROUP BY ser.series_id''', (series_id,)).fetchone()
    c.close()
    if row:
        return row['total_seasons']
    else:
        return 0


def get_seasons(series_id, only_last = False):
    c = _database.cursor()
    if only_last:
        return c.execute('''SELECT DISTINCT sea.*,ser.title AS series_title
                        FROM season AS sea
                        JOIN series AS ser ON ser.series_id = sea.series_id
                        WHERE ser.series_id = (?)
                        ORDER BY season_no DESC LIMIT 1''', (series_id,))
    else:
        return c.execute('''SELECT DISTINCT sea.*,ser.title AS series_title
                        FROM season AS sea
                        JOIN series AS ser ON ser.series_id = sea.series_id
                        WHERE ser.series_id = (?)
                        ORDER BY season_no ASC''', (series_id,))


def get_episodes(season_id):
    c = _database.cursor()
    return c.execute('''SELECT DISTINCT e.*,
        sea.season_no AS season_no,
        sea.url AS season_url,
        ser.title AS series_title,
        ser.series_id AS series_id
        FROM episode AS e
        JOIN season AS sea ON sea.season_id = e.season_id
        JOIN series AS ser ON ser.series_id = sea.series_id
        WHERE sea.season_id = (?)''', (season_id,))


def get_types(col):
    c = _database.cursor()
    items = c.execute('select distinct %s from series' % col)
    list = []
    for data in items:
        data = data[0]
        if type(data) == type(str()):
            if 'Rated' in data:
                item = data.split('for')[0]
                if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                    list.append(item)
            else:
                data = data.decode('utf-8').encode('utf-8').split(',')
                for item in data:
                    item = item.replace('& ', '').strip()
                    if item not in list and item <> '' and item <> 0 and item <> 'Inc.' and item <> 'LLC.':
                        list.append(item)
        elif data <> 0:
            if data is not None:
                list.append(str(data))
    c.close()
    return list


def update_series_list(force=False):
    # Check if we've recently updated and skip
    if not force and not _needs_update():
        return

    dialog = xbmcgui.DialogProgress()
    dialog.create('Refreshing TV Database')
    dialog.update(0, 'Initializing TV Scan')

    url = '{0}/internet/'.format(db_common.WEB_DOMAIN)
    data = connection.get_url(url)
    tree = BeautifulSoup(data, 'html.parser')

    shows = tree.find_all('td', attrs={'class':'mnlcategorylist'})
    total = len(shows)
    count = 0

    for show in shows:
        count += 1
        dialog.update(0, 'Scanned {0} of {1} tv shows'.format(count, total))

        link = show.find('a')
        title = common.normalize_string(link.find('b').string).strip()
        url = '{0}/internet/{1}'.format(db_common.WEB_DOMAIN, link['href'])

        insert_series(title, url)

    _set_last_update()


def update_series(series, force=False):
    data = connection.get_url(series['url'])
    tree = BeautifulSoup(data, 'html.parser')

    seasons = tree.find_all('td', attrs={'class':'mnlcategorylist'})

    for season in seasons:
        link = season.find('a')
        title = common.normalize_string(link.find('b').string).strip()
        url = '{0}{1}'.format(series['url'], link['href'])

        season_no = 0
        m = re.search('Season ([0-9]+)', title)
        if m:
            season_no = m.group(1)
        else:
            # For now don't import specials. Perhaps make this an option later
            continue

        insert_season(series['series_id'], title, url, season_no)


def update_season(season, force=False):
    data = connection.get_url(season['url'])
    if data is False:
        common.notification('Error Updating Season Data')
        return

    tree = BeautifulSoup(data, 'html.parser')

    c = _database.cursor()
    c.execute("DELETE FROM episode WHERE season_id = ?", (season['season_id'],))
    c.close()

    episodes = tree.find_all('tr', attrs={'class': '3'})
    for episode_tr in episodes:
        episode_td = episode_tr.find('td', attrs={'class': 'episode'})

        skip = False;
        for children in episode_td.stripped_strings:
            # Only export aired episodes
            if 'Next Episode:' in children:
                skip = True
                break

        if skip:
            continue

        episode_m = re.search('^e([0-9]+)$', episode_td.find('a')['name'])
        episode_no = episode_m.group(1)

        title = common.normalize_string(episode_td.find('b').string).strip()

        air_date_td = episode_tr.find('td', attrs={'align': 'right'})
        air_date_value = air_date_td.find('div').string
        air_date_value = air_date_value[air_date_value.find(': ')+2:]
        air_date = common.parse_date(air_date_value, '%d %B %Y')

        insert_episode(season['season_id'], title, episode_no, None, air_date)


def get_media_urls(season_url, episode_title):

    html = connection.get_url(season_url)

    sources = []

    #Search within HTML to only get portion of links specific to episode requested
    r = re.search('<td class="episode"><a name=".+?"></a><b>%s</b>(.+?)(<a name=|<p align="center">)' % re.escape(episode_title), html, re.DOTALL)
    if r:
        html = r.group(1)
    else:
        return False

    match = re.compile('''<a onclick=.+? href=".+?id=(.+?)" target=.+?<div>.+?(|part [0-9]* of [0-9]*)</div>.+?<span class='.*?'>(.*?)</span>.+?Host: (.+?)<br/>.+?class="report">.+?([0-9]*[0-9]%) Said Work''',re.DOTALL).findall(html)
    for linkid, vidname, load, host, working in match:
        if vidname:
           vidname = vidname.title()
        else:
           vidname = 'Full'
        sources.append({
            'host': host,
            'media_id': linkid,
            'title': vidname + ' - ' + host + ' - ' + load + ' - ' + working
        })

    return sources


def _needs_update():
    # Update every 15 days
    if 'last_series_list_update' in _database_meta:
        last_update = common.parse_date(_database_meta['last_series_list_update'], '%Y-%m-%d')
        return (date.today() - last_update.date()).days > 15

    return True


def _set_last_update():
    _database_meta['last_series_list_update'] = date.today().strftime('%Y-%m-%d')
    _write_meta_file()


def _write_meta_file():
    f = open(DB_META_FILE, 'w')
    json.dump(_database_meta, f)
    f.close()


DB_META_FILE = os.path.join(common.__addonprofile__, 'tv.meta')
_database_meta = False
if os.path.exists(DB_META_FILE):
    f = open(DB_META_FILE, 'r')
    _database_meta = json.load(f)
    f.close()
else:
    _database_meta = {}

DB_FILE = os.path.join(common.__addonprofile__, 'tv.db')

_database = sqlite.connect(DB_FILE)
_database.text_factory = str
_database.row_factory = sqlite.Row
_database.create_function("REGEXP", 2, db_common.re_fn)
create()

