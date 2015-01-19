#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import urllib

import xbmcplugin
import xbmc
import xbmcgui
import xbmcaddon
import common
import database_movies as movies_db
import database_common


pluginhandle = common.pluginHandle

# 501-POSTER WRAP 503-MLIST3 504=MLIST2 508-FANARTPOSTER 
confluence_views = [500, 501, 502, 503, 504, 508]

################################ Movie listing
def list_movie_root():
    movies_db.update_movies(False)

    cm = []
    if common.get_setting('enablelibrary') == 'true':
        cm_u = sys.argv[0] + '?mode=movies&sitemode=list_movies_favor_filtered_export'
        cm = [('Export Favorites to Library', 'XBMC.RunPlugin(%s)' % cm_u)]

    common.add_directory('Favorites', 'movies', 'list_movies_favor_filtered', contextmenu=cm)

    cm = []
    if common.get_setting('enablelibrary') == 'true':
        cm_u = sys.argv[0] + '?mode=movies&sitemode=list_movies_export'
        cm = [('Export All to Library', 'XBMC.RunPlugin(%s)' % cm_u)]

    common.add_directory('All Movies', 'movies', 'list_movies', contextmenu=cm)

    common.add_directory('Genres', 'movies', 'list_movie_types', 'GENRE')
    common.add_directory('Years', 'movies', 'list_movie_types', 'YEARS')
    common.add_directory('Studios', 'movies', 'list_movie_types', 'STUDIOS')
    common.add_directory('MPAA Rating', 'movies', 'list_movie_types', 'MPAA')
    common.add_directory('Directors', 'movies', 'list_movie_types', 'DIRECTORS')
    common.add_directory('Actors', 'movies', 'list_movie_types', 'ACTORS')
    # common.add_directory('Recently Added', 'movies', 'list_movies_recent_filtered', 'ACTORS')
    common.add_directory('Watched', 'movies', 'list_movies_watched_filtered')
    xbmcplugin.endOfDirectory(pluginhandle)


def list_movie_types(type=False):
    if not type:
        type = common.args.url
    if type == 'GENRE':
        mode = 'list_movies_genre_filtered'
        items = movies_db.get_types('genres')
    elif type == 'STUDIOS':
        mode = 'list_movies_studio_filtered'
        items = movies_db.get_types('studio')
    elif type == 'YEARS':
        mode = 'list_movies_year_filtered'
        items = movies_db.get_types('year')
    elif type == 'DIRECTORS':
        mode = 'list_movies_director_filtered'
        items = movies_db.get_types('director')
    elif type == 'MPAA':
        mode = 'list_movies_mpaa_filtered'
        items = movies_db.get_types('mpaa')
    elif type == 'ACTORS':
        mode = 'list_movies_actor_filtered'
        items = movies_db.get_types('actors')

    for item in items:
        common.add_directory(item, 'movies', mode, item)

    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle, updateListing=False)


def list_movies_genre_filtered():
    list_movies(export=False, genrefilter=common.args.url)


def list_movies_year_filtered():
    list_movies(export=False, yearfilter=common.args.url)


def list_movies_mpaa_filtered():
    list_movies(export=False, mpaafilter=common.args.url)


def list_movies_studio_filtered():
    list_movies(export=False, studiofilter=common.args.url)


def list_movies_director_filtered():
    list_movies(export=False, directorfilter=common.args.url)


def list_movies_actor_filtered():
    list_movies(export=False, actorfilter=common.args.url)


def list_movies_watched_filtered():
    list_movies(export=False, watchedfilter=True)


def list_movies_recent_filtered():
    list_movies(export=False, watchedfilter=True)


def list_movies_favor_filtered():
    list_movies(export=False, favorfilter=True)


def list_movies_favor_filtered_export():
    list_movies(export=True, favorfilter=True)


def list_movies_export():
    list_movies(export=True)


def list_movies(export=False, genrefilter=False, actorfilter=False, directorfilter=False, studiofilter=False,
                yearfilter=False, mpaafilter=False, watchedfilter=False, favorfilter=False, alphafilter=False):
    if export:
        import xbmclibrary

        xbmclibrary.setup_library()

    movies = movies_db.get_movies(genrefilter=genrefilter, actorfilter=actorfilter, directorfilter=directorfilter,
                                 studiofilter=studiofilter, yearfilter=yearfilter, mpaafilter=mpaafilter,
                                 watchedfilter=watchedfilter, favorfilter=favorfilter,
                                 alphafilter=alphafilter).fetchall()
    total = len(movies)
    for moviedata in movies:
        if export:
            xbmclibrary.export_movie(moviedata)
        else:
            _add_movie_item(moviedata, total)

    if export:
        common.notification('Export Complete')
        if common.get_setting('updatelibraryafterexport') == 'true':
            xbmclibrary.update_xbmc_library()

    else:
        xbmcplugin.setContent(pluginhandle, 'Movies')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_RUNTIME)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_MPAA_RATING)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DURATION)
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
        xbmcplugin.endOfDirectory(pluginhandle)

        viewenable = common.get_setting("viewenable")
        if viewenable == 'true' and common.get_setting("movieview"):
            view = int(common.get_setting("movieview"))
            xbmc.executebuiltin("Container.SetViewMode(" + str(confluence_views[view]) + ")")


def _add_movie_item(data, total=0):
    fanart = database_common.get_thumb(data['content_id'])
    poster = database_common.get_poster(data['content_id'])

    labels = {
        'title': data['title'],
        'sorttitle': data['title_sort'],
        'year': data['year'],
        'studio': data['studio'],
        'duration': data['duration'],
        'playcount': data['playcount'],
        'plot': data['plot']
    }

    if data['mpaa']:
        labels['mpaa'] = 'Rated ' + data['mpaa']
    if data['directors']:
        labels['director'] = ' / '.join(data['directors'].split(','))
    if data['genres']:
        labels['genre'] = ' / '.join(data['genres'].split(','))
    if data['actors']:
        labels['cast'] = data['actors'].split(',')

    item = xbmcgui.ListItem(data['title'], data['mpaa'], iconImage=poster, thumbnailImage=poster)
    item.setInfo(type='Video', infoLabels=labels)
    item.setProperty('fanart_image', fanart)

    try:
        if data['is_hd']:
            item.addStreamInfo('video', {'codec': 'h264', 'width': 1280, 'height': 720, 'duration': data['duration']})
        else:
            item.addStreamInfo('video', {'codec': 'h264', 'width': 720, 'height': 400, 'duration': data['duration']})

        if data['audio_type'] == '5.1 Surround':
            item.addStreamInfo('audio', {'codec': 'aac', 'channels': 6})
        else:
            item.addStreamInfo('audio', {'codec': 'aac', 'channels': 2})

        if data['cc_available']:
            item.addStreamInfo('subtitle', {'language': 'en'})

    except:
        pass

    contextmenu = []
    if data['favor']:
        cm_u = sys.argv[0] + '?url={0}&mode=movies&sitemode=unfavor&title={1}'.format(data['content_id'],
                                                                                      urllib.unquote_plus(
                                                                                          data['title']))
        contextmenu.append((common.localise(39006), 'XBMC.RunPlugin(%s)' % cm_u))
    else:
        cm_u = sys.argv[0] + '?url={0}&mode=movies&sitemode=favor&title={1}'.format(data['content_id'],
                                                                                    urllib.unquote_plus(data['title']))
        contextmenu.append((common.localise(39007), 'XBMC.RunPlugin(%s)' % cm_u))

    if data['playcount'] > 0:
        cm_u = sys.argv[0] + '?url={0}&mode=movies&sitemode=unwatch'.format(data['content_id'])
        contextmenu.append(('Mark as unwatched', 'XBMC.RunPlugin(%s)' % cm_u))
    else:
        cm_u = sys.argv[0] + '?url={0}&mode=movies&sitemode=watch'.format(data['content_id'])
        contextmenu.append(('Mark as watched', 'XBMC.RunPlugin(%s)' % cm_u))

    contextmenu.append(('Movie Information', 'XBMC.Action(Info)'))

    item.addContextMenuItems(contextmenu)

    u = sys.argv[0] + '?url={0}&mode=movies&sitemode=play_movie&content_id={1}'.format(data['url'], data['content_id'])

    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=False, totalItems=total)


def play_movie():
    url = common.args.url
    content_id = int(common.args.content_id)
    kiosk = 'true'

    item = xbmcgui.ListItem()
    if movies_db.watch(content_id) > 0:
        common.refresh_menu()
        xbmc.executebuiltin("RunPlugin(plugin://plugin.program.chrome.launcher/?url=" + urllib.quote_plus(
            url) + "&mode=showSite&kiosk=" + kiosk + ")")

        # We assume the URL is still valid if it's in our database
        xbmcplugin.setResolvedUrl(common.pluginHandle, True, item)

    else:
        xbmcplugin.setResolvedUrl(common.pluginHandle, False, item)


##########################################
# Context Menu Links
##########################################
def refresh_db():
    movies_db.update_movies(True)


def favor():
    content_id = common.args.url
    if movies_db.favor(content_id) > 0:
        common.notification('Added ' + urllib.unquote_plus(common.args.title) + ' to favorites')
        common.refresh_menu()
    else:
        common.notification('Error adding movie to favorites', isError=True)


def unfavor():
    content_id = common.args.url
    if movies_db.unfavor(content_id) > 0:
        common.notification('Removed ' + urllib.unquote_plus(common.args.title) + ' from favorites')
        common.refresh_menu()
    else:
        common.notification('Error removing movie from favorites', isError=True)


def watch():
    content_id = common.args.url
    if movies_db.watch(content_id) > 0:
        common.refresh_menu()
    else:
        common.notification('Could not update watch count', isError=True)


def unwatch():
    content_id = common.args.url
    movies_db.unwatch(content_id)
    common.refresh_menu()

        

