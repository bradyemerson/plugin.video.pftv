#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
from datetime import date, datetime
import time
from sqlite3 import dbapi2 as sqlite

import simplejson as json

import xbmcgui
import common
import connection
import database_common as db_common
from bs4 import BeautifulSoup


def create():
    c = _database.cursor()
    c.execute('''CREATE TABLE movies
                (content_id INTEGER PRIMARY KEY,
                 media_id TEXT,
                 url TEXT,
                 title TEXT,
                 title_sort TEXT,
                 plot TEXT,
                 duration INTEGER,
                 year INTEGER,
                 studio TEXT,
                 mpaa TEXT,
                 directors TEXT,
                 actors TEXT,
                 genres TEXT,
                 popularity INTEGER,
                 added_date timestamp,
                 cc_available BOOLEAN,
                 is_hd BOOLEAN,
                 audio_type TEXT,
                 playcount INTEGER DEFAULT 0,
                 favor BOOLEAN DEFAULT 0,
                 in_last_update BOOLEAN DEFAULT 1)''')
    _database.commit()
    c.close()


def insert(content_id, media_id, url=None, title=None, title_sort=None, plot=None, duration=None, year=None,
           studio=None, mpaa=None,
           directors=None, actors=None, genres=None, popularity=None, added_date=None, cc_available=False,
           is_hd=False, audio_type=None):
    c = _database.cursor()

    c.execute('''INSERT OR REPLACE INTO movies (
                 content_id,
                 media_id,
                 url,
                 title,
                 title_sort,
                 plot,
                 duration,
                 year,
                 studio,
                 mpaa,
                 directors,
                 actors,
                 genres,
                 popularity,
                 added_date,
                 cc_available,
                 is_hd,
                 audio_type,
                 playcount,
                 favor,
                 in_last_update) VALUES (
                 :content_id,
                 :media_id,
                 :url,
                 :title,
                 :title_sort,
                 :plot,
                 :duration,
                 :year,
                 :studio,
                 :mpaa,
                 :directors,
                 :actors,
                 :genres,
                 :popularity,
                 :added_date,
                 :cc_available,
                 :is_hd,
                 :audio_type,
                 (SELECT playcount FROM movies WHERE content_id = :content_id),
                 (SELECT favor FROM movies WHERE content_id = :content_id),
                 :in_last_update)''', {
        'content_id': int(content_id),
        'media_id': media_id,
        'url': url,
        'title': title,
        'title_sort': title_sort,
        'plot': plot,
        'duration': duration,
        'year': year,
        'studio': studio,
        'mpaa': mpaa,
        'directors': directors,
        'actors': actors,
        'genres': genres,
        'popularity': popularity,
        'added_date': added_date,
        'cc_available': cc_available,
        'is_hd': is_hd,
        'audio_type': audio_type,
        'in_last_update': True
    })
    _database.commit()
    c.close()


def get_movie(content_id):
    c = _database.cursor()
    return c.execute('SELECT DISTINCT * FROM movies WHERE content_id = (?)', (content_id,))


def delete(content_id):
    c = _database.cursor()
    c.execute('DELETE FROM movies WHERE content_id = (?)', (content_id,))
    c.close()


def watch(content_id):
    # TODO make this actually increment
    c = _database.cursor()
    c.execute("UPDATE movies SET playcount = 1 WHERE content_id = (?)", (content_id,))
    _database.commit()
    c.close()
    return c.rowcount


def unwatch(content_id):
    c = _database.cursor()
    c.execute("UPDATE movies SET playcount=? WHERE content_id = (?)", (0, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def favor(content_id):
    c = _database.cursor()
    c.execute("UPDATE movies SET favor=? WHERE content_id=?", (True, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def unfavor(content_id):
    c = _database.cursor()
    c.execute("UPDATE movies SET favor=? WHERE content_id=?", (False, content_id))
    _database.commit()
    c.close()
    return c.rowcount


def get_movies(genrefilter=False, actorfilter=False, directorfilter=False, studiofilter=False, yearfilter=False,
               mpaafilter=False, watchedfilter=False, favorfilter=False, alphafilter=False):
    c = _database.cursor()
    if genrefilter:
        genrefilter = '%' + genrefilter + '%'
        return c.execute('SELECT DISTINCT * FROM movies WHERE genres LIKE (?)',
                         (genrefilter,))
    elif mpaafilter:
        return c.execute('SELECT DISTINCT * FROM movies WHERE mpaa = (?)', (mpaafilter,))
    elif actorfilter:
        actorfilter = '%' + actorfilter + '%'
        return c.execute('SELECT DISTINCT * FROM movies WHERE actors LIKE (?)',
                         (actorfilter,))
    elif directorfilter:
        return c.execute('SELECT DISTINCT * FROM movies WHERE directors LIKE (?)',
                         (directorfilter,))
    elif studiofilter:
        return c.execute('SELECT DISTINCT * FROM movies WHERE studio = (?)', (studiofilter,))
    elif yearfilter:
        return c.execute('SELECT DISTINCT * FROM movies WHERE year = (?)', (int(yearfilter),))
    elif watchedfilter:
        return c.execute('SELECT DISTINCT * FROM movies WHERE playcount > 0')
    elif favorfilter:
        return c.execute('SELECT DISTINCT * FROM movies WHERE favor = 1')
    elif alphafilter:
        return c.execute('SELECT DISTINCT * FROM movies WHERE title REGEXP (?)',
                         (alphafilter + '*',))
    else:
        return c.execute('SELECT DISTINCT * FROM movies')


def get_types(col):
    c = _database.cursor()
    items = c.execute('select distinct %s from movies' % col)
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


def update_movies(force=False):
    # Check if we've recently updated and skip
    global audio_type
    if not force and not _needs_update():
        return

    dialog = xbmcgui.DialogProgress()
    dialog.create('Refreshing Movie Database')
    dialog.update(0, 'Initializing Movie Scan')

    data = connection.get_url(db_common.WEB_DOMAIN + '/Movies')
    tree = BeautifulSoup(data, 'html.parser')
    movies_html = tree.find(attrs={'id': 'work-items'}).findAll('div', recursive=False,
                                                                attrs={'class': 'item', 'context': 'Movies'})

    del tree
    del data

    json_url = '{0}/metadata-service/play/content/partner/Web_{1}.json?contentType=Movie'.format(db_common.API_DOMAIN, db_common.SERVICE)
    data = connection.get_url(json_url)
    movies_json = json.loads(data)['playContentArray']['playContents']

    # Mark all movies as unfound. This will be updated as we go through
    c = _database.cursor()
    c.execute("UPDATE movies SET in_last_update = 0")
    _database.commit()
    c.close()

    total = len(movies_html)
    count = 0

    for movie in movies_html:
        count += 1
        dialog.update(0, 'Scanned {0} of {1} movies'.format(count, total))

        content_id = int(movie['catalogid'])

        playLinkElem = movie.find('a', attrs={'class': 'collectionPlay'})
        url = db_common.WEB_DOMAIN + playLinkElem['href']

        genreList = []
        genreLI = movie.find('ul', attrs={'class': 'genres'}).findAll('li', recursive=False)
        for genre in genreLI:
            genreList.append(genre.string)
        genres = ','.join(genreList)

        # Find the movie in the json for the remainder of content
        for movie_json in movies_json:
            if (movie_json['contentId'] == content_id):
                media_id = movie_json['mediaId']
                title = movie_json['title']
                runtime = int(movie_json['runtime'] / 60)
                year = int(movie_json['releaseYear'])
                plot = movie_json['logLine']
                studio = movie_json['studio']
                popularity = movie_json['popularity']
                title_sort = movie_json['titleSort']
                cc_available = movie_json['closedCaption']
                audio_type = movie_json['audioType']
                is_hd = movie_json['hd']
                mpaa = db_common.parse_mpaa(movie_json['mpaaRating'])

                try:
                    date_without_time = movie_json['startDate'][:10]
                    added_date = datetime.strptime(date_without_time, '%Y-%m-%d')
                except TypeError:
                    added_date = datetime(*(time.strptime(date_without_time, '%Y-%m-%d')[0:6]))

                actors_list = []
                for actor in movie_json['actors']:
                    actors_list.append(actor['fullName'])

                actors = ','.join(actors_list)

                directors_list = []
                for director in movie_json['directors']:
                    directors_list.append(director['fullName'])

                directors = ','.join(directors_list)

                break

        insert(content_id=content_id, media_id=media_id, url=url, title=title, title_sort=title_sort, plot=plot,
               duration=runtime, year=year, mpaa=mpaa, popularity=popularity, added_date=added_date,
               audio_type=audio_type, actors=actors, directors=directors, genres=genres, studio=studio,
               cc_available=cc_available, is_hd=is_hd)

        # Preload images
        db_common.get_poster(content_id)
        db_common.get_thumb(content_id)

    _set_last_update()

    # Find unfound movies and remove them
    c = _database.cursor()
    c.execute("DELETE FROM movies WHERE in_last_update = 0")
    c.close()


def _needs_update():
    # Update every 15 days
    if 'last_update' in _database_meta:
        # http://forum.kodi.tv/showthread.php?tid=112916
        try:
            last_update = datetime.strptime(_database_meta['last_update'], '%Y-%m-%d')
        except TypeError:
            last_update = datetime(*(time.strptime(_database_meta['last_update'], '%Y-%m-%d')[0:6]))
        return (date.today() - last_update.date()).days > 15

    return True


def _set_last_update():
    _database_meta['last_update'] = date.today().strftime('%Y-%m-%d')
    _write_meta_file()


def _write_meta_file():
    f = open(DB_META_FILE, 'w')
    json.dump(_database_meta, f)
    f.close()


DB_META_FILE = os.path.join(common.__addonprofile__, 'movies.meta')
_database_meta = False
if os.path.exists(DB_META_FILE):
    f = open(DB_META_FILE, 'r')
    _database_meta = json.load(f)
    f.close()
else:
    _database_meta = {}

DB_FILE = os.path.join(common.__addonprofile__, 'movies.db')
if not os.path.exists(DB_FILE):
    _database = sqlite.connect(DB_FILE)
    _database.text_factory = str
    _database.row_factory = sqlite.Row
    create()
else:
    _database = sqlite.connect(DB_FILE)
    _database.text_factory = str
    _database.row_factory = sqlite.Row
