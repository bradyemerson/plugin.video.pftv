#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import sys
import string

import xbmc
import xbmcgui
import resources.lib.common as common
import database_tv as tv_db
from bs4 import BeautifulSoup

import listtv

pluginhandle = common.pluginHandle

if common.get_setting('libraryfolder') == '0':
    MOVIE_PATH = os.path.join(xbmc.translatePath(common.__addonprofile__), 'Movies')
    TV_SHOWS_PATH = os.path.join(xbmc.translatePath(common.__addonprofile__), 'TV')
else:  # == 1
    if common.get_setting('customlibraryfolder') != '':
        MOVIE_PATH = os.path.join(xbmc.translatePath(common.get_setting('customlibraryfolder')), 'Movies')
        TV_SHOWS_PATH = os.path.join(xbmc.translatePath(common.get_setting('customlibraryfolder')), 'TV')
    else:
        xbmcgui.Dialog().ok("Error", "Set location of custom folder or use built in folder")
        common.open_settings()


def setup_library():
    if common.get_setting('autoaddfolders') != 'yes':
        common.notification('Starting Export', 10000)
        return False

    source_path = os.path.join(xbmc.translatePath('special://profile/'), 'sources.xml')
    dialog = xbmcgui.Dialog()

    # ensure the directories exist
    _create_directory(MOVIE_PATH)
    _create_directory(TV_SHOWS_PATH)

    try:
        file = open(source_path, 'r')
        content = file.read()
        file.close()
    except:
        # TODO Provide a Yes/No option here
        dialog.ok("Error adding new sources ", "Could not read from sources.xml, does it really exist?")
        return False

    soup = BeautifulSoup(content)
    video = soup.find("video")

    added_new_paths = False

    if len(soup.find_all('name', text='PFTV Movies')) < 1:
        movie_source_tag = soup.new_tag('source')

        movie_name_tag = soup.new_tag('name')
        movie_name_tag.string = 'PFTV Movies'
        movie_source_tag.insert(0, movie_name_tag)

        movie_path_tag = soup.new_tag('path', pathversion='1')
        movie_path_tag.string = MOVIE_PATH
        movie_source_tag.insert(1, movie_path_tag)

        movie_sharing = soup.new_tag('allowsharing')
        movie_sharing.string = 'true'
        movie_source_tag.insert(2, movie_sharing)

        video.append(movie_source_tag)
        added_new_paths = True

    if len(soup.find_all('name', text='PFTV TV')) < 1:
        tv_source_tag = soup.new_tag('source')

        tvshow_name_tag = soup.new_tag('name')
        tvshow_name_tag.string = 'PFTV TV'
        tv_source_tag.insert(0, tvshow_name_tag)

        tvshow_path_tag = soup.new_tag('path', pathversion='1')
        tvshow_path_tag.string = TV_SHOWS_PATH
        tv_source_tag.insert(1, tvshow_path_tag)

        tvshow_sharing = soup.new_tag('allowsharing')
        tvshow_sharing.string = 'true'
        tv_source_tag.insert(2, tvshow_sharing)

        video.append(tv_source_tag)
        added_new_paths = True

    if added_new_paths:
        file = open(source_path, 'w')
        file.write(str(soup))
        file.close()

    common.notification('Starting Export', 10000)

    return added_new_paths


def update_xbmc_library():
    xbmc.executebuiltin("UpdateLibrary(video)")


def complete_export(added_folders):
    if added_folders:
        xbmcgui.Dialog() \
            .ok("Added PFTV Folders to Video Sources",
                "Two steps are required to complete the process:",
                "1. Kodi must be restarted",
                "2. After restarting, you must configure the content type of the PFTV folders in the File section"
            )
    else:
        common.notification('Export Complete')
        if common.get_setting('updatelibraryafterexport') == 'true':
            update_xbmc_library()


def export_movie(data):
    if data['year']:
        filename = _clean_filename(data['title'] + ' (' + str(data['year']) + ')')
    else:
        filename = _clean_filename(data['title'])

    strm_file = filename + ".strm"
    u = sys.argv[0] + '?url={0}&mode=movies&sitemode=play_movie&content_id={1}'.format(data['url'], data['content_id'])
    _save_file(strm_file, u, MOVIE_PATH)


def export_series(series):
    tv_db.update_series(series)
    seasons = tv_db.get_seasons(series['series_id'], True)

    dirname = _get_series_dir(series)
    for season in seasons:
        tv_db.update_season(season)
        export_season(season, dirname)


def export_season(season, series_dir=None):
    episodes = tv_db.get_episodes(season['season_id'])
    dirname = _get_season_dir(season, series_dir)
    for episode in episodes:
        export_episode(episode, dirname)


def export_episode(episode, season_dir=None):
    if season_dir is None:
        season = tv_db.lookup_season(episode['season_id']).fetchone()
        season_dir = _get_season_dir(season)

    filename = 'S{0:02d}E{1:02d} - {2}'.format(episode['season_no'], episode['episode_no'], _clean_filename(episode['title']))

    strm_file = filename + ".strm"
    u = listtv.create_play_link(episode)
    _save_file(strm_file, u, season_dir)


def _get_series_dir(series):
    dirname = os.path.join(TV_SHOWS_PATH, _clean_filename(series['title']))
    _create_directory(dirname)
    return dirname


def _get_season_dir(season, series_dir=None):
    if series_dir is None:
        series = tv_db.lookup_series(season['series_id']).fetchone()
        series_dir = _get_series_dir(series)

    dirname = os.path.join(series_dir, 'Season {0}'.format(season['season_no']))
    _create_directory(dirname)
    return dirname


def _save_file(filename, data, dir):
    path = os.path.join(dir, filename)
    file = open(path, 'w')
    file.write(data)
    file.close()


def _create_directory(dir_path):
    dir_path = dir_path.strip()
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def _clean_filename(name):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    return ''.join(c for c in name if c in valid_chars)

