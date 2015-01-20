#!/usr/bin/env python
# -*- coding: utf-8 -*-
import string
import sys
import urllib

import xbmcplugin
import xbmcgui
import common
import database_tv as tv_db


pluginhandle = common.pluginHandle

###################### Television

def list_tv_root():
    tv_db.update_series_list(False)

    cm_u = sys.argv[0] + '?mode=tv&sitemode=list_tvshows_favor_filtered_export'
    cm = [('Export Favorites to Library', 'XBMC.RunPlugin(%s)' % cm_u)]
    common.add_directory('Favorites', 'tv', 'list_tvshows_favor_filtered', contextmenu=cm)

    cm = []
    cm_u = sys.argv[0] + '?mode=tv&sitemode=list_tvshows_export&url=""'
    # cm.append(('Export All to Library', 'XBMC.RunPlugin(%s)' % cm_u))
    cm.append(('Force TV Series Refresh', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=tv&sitemode=refresh_db')))
    common.add_directory('All Shows', 'tv', 'list_tvshows_az', contextmenu=cm)

    # common.add_directory('Genres', 'tv', 'list_tvshow_types', 'GENRE')
    #common.add_directory('Years', 'tv', 'list_tvshow_types', 'YEARS')
    #common.add_directory('TV Rating', 'tv', 'list_tvshow_types', 'MPAA')
    #common.add_directory('Actors', 'tv', 'list_tvshow_types', 'ACTORS')
    #common.add_directory('Watched', 'tv', 'list_tvshows_watched_filtered')
    xbmcplugin.endOfDirectory(pluginhandle)


def list_tvshows_az():
    common.add_directory('#', 'tv', 'list_tvshow_alpha_filtered', '#')

    for letter in string.uppercase:
        common.add_directory(letter, 'tv', 'list_tvshow_alpha_filtered', letter)

    xbmcplugin.endOfDirectory(pluginhandle)


def list_tvshow_types(type=False):
    if not type:
        type = common.args.url

    if type == 'GENRE':
        mode = 'list_tvshows_genre_filtered'
        items = tv_db.get_types('genres')
    elif type == 'YEARS':
        mode = 'list_tvshows_years_filtered'
        items = tv_db.get_types('year')
    elif type == 'MPAA':
        mode = 'list_tvshows_mpaa_filtered'
        items = tv_db.get_types('mpaa')
    elif type == 'ACTORS':
        mode = 'list_tvshows_actors_filtered'
        items = tv_db.get_types('actors')

    for item in items:
        common.add_directory(item, 'tv', mode, item)

    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(pluginhandle)


def list_tvshows_genre_filtered():
    list_tvshows(export=False, genrefilter=common.args.url)


def list_tvshows_years_filtered():
    list_tvshows(export=False, yearfilter=common.args.url)


def list_tvshows_mpaa_filtered():
    list_tvshows(export=False, mpaafilter=common.args.url)


def list_tvshows_creators_filtered():
    list_tvshows(export=False, creatorfilter=common.args.url)


def list_tvshows_favor_filtered_export():
    list_tvshows(export=True, favorfilter=True)


def list_tvshows_favor_filtered():
    list_tvshows(export=False, favorfilter=True)


def list_tvshows_export():
    list_tvshows(export=True)


def list_tvshow_alpha_filtered():
    letter = common.args.url
    list_tvshows(alphafilter=letter)


def list_tvshows(export=False, mpaafilter=False, genrefilter=False, creatorfilter=False, yearfilter=False,
                 favorfilter=False, alphafilter=False):
    if export:
        import xbmclibrary
        added_folders = xbmclibrary.setup_library()

    shows = tv_db.get_series(favorfilter=favorfilter,alphafilter=alphafilter).fetchall()
    total = len(shows)

    for showdata in shows:
        if export:
            xbmclibrary.export_series(showdata)
        else:
            _add_series_item(showdata, total)

    if export:
        xbmclibrary.complete_export(added_folders)

    else:
        xbmcplugin.setContent(pluginhandle, 'tvshows')
        xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
        # xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        # xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_MPAA_RATING)
        # xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_STUDIO_IGNORE_THE)
        xbmcplugin.endOfDirectory(pluginhandle)


def _add_series_item(data, total=0):
    total_seasons = tv_db.get_series_season_count(data['series_id'])

    labels = {
        'title': data['title'],
        'tvshowtitle': data['title'],
        'studio': data['studio'],
        'year': data['year']
    }

    if data['directors']:
        labels['director'] = ' / '.join(data['directors'].split(','))
    if data['genres']:
        labels['genres'] = ' / '.join(data['genres'].split(','))
    if data['actors']:
        labels['cast'] = data['actors'].split(',')

    item = xbmcgui.ListItem(data['title'])
    item.setInfo(type='Video', infoLabels=labels)
    item.setProperty('TotalSeasons', str(total_seasons))

    contextmenu = []
    if data['favor']:
        cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=unfavor_series&title={1}'.format(data['series_id'],
                                                                                         urllib.unquote_plus(
                                                                                             data['title']))
        contextmenu.append((common.localise(39006), 'XBMC.RunPlugin(%s)' % cm_u))
    else:
        cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=favor_series&title={1}'.format(data['series_id'],
                                                                                       urllib.unquote_plus(
                                                                                           data['title']))
        contextmenu.append((common.localise(39007), 'XBMC.RunPlugin(%s)' % cm_u))

    cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=update_series'.format(data['series_id'])
    contextmenu.append(('Force Series Update', 'XBMC.RunPlugin(%s)' % cm_u))

    item.addContextMenuItems(contextmenu)

    u = sys.argv[0] + '?url={0}&mode=tv&sitemode=list_tv_seasons'.format(data['series_id'])
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=True, totalItems=total)


def list_tv_seasons():
    series_id = common.args.url

    series = tv_db.lookup_series(series_id).fetchone()
    tv_db.update_series(series)

    seasons = tv_db.get_seasons(series_id).fetchall()
    total = len(seasons)

    for season in seasons:
        _add_season_item(season, total)

    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.setContent(pluginhandle, 'tvshows')
    xbmcplugin.endOfDirectory(pluginhandle)


def _add_season_item(data, total=0):
    labels = {
        'title': data['title'],
        'tvshowtitle': data['series_title'],
        'season': data['season_no']
    }

    item = xbmcgui.ListItem(data['title'])
    item.setInfo(type='Video', infoLabels=labels)

    contextmenu = []
    cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=export_season'.format(data['season_id'])
    contextmenu.append(('Export Season to Library', 'XBMC.RunPlugin(%s)' % cm_u))
    cm_u = sys.argv[0] + '?url={0}&mode=tv&sitemode=update_season'.format(data['season_id'])
    contextmenu.append(('Force Season Update', 'XBMC.RunPlugin(%s)' % cm_u))
    item.addContextMenuItems(contextmenu)

    u = sys.argv[0] + '?url={0}&mode=tv&sitemode=list_episodes'.format(data['season_id'])
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=True, totalItems=total)


def list_episodes(export=False):
    season_id = common.args.url

    season = tv_db.lookup_season(season_id).fetchone()
    tv_db.update_season(season)

    episodes = tv_db.get_episodes(season_id).fetchall()
    total = len(episodes)

    for episode in episodes:
        _add_episode_item(episode, total)

    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_VIDEO_SORT_TITLE)
    xbmcplugin.setContent(pluginhandle, 'Episodes')
    xbmcplugin.endOfDirectory(pluginhandle)


def _add_episode_item(data, total):
    labels = {
        'title': data['title'],
        'tvshowtitle': data['series_title'],
        'season': data['season_no'],
        'episode': data['episode_no'],
        'playcount': data['play_count']
    }

    if data['air_date']:
        labels['year'] = data['air_date'][:4]
        labels['aired'] = data['air_date'][:10]

    item = xbmcgui.ListItem(data['title'])
    item.setInfo(type='Video', infoLabels=labels)

    contextmenu = []

    #if data['play_count'] > 0:
    #    cm_u = sys.argv[0] + '?url={0}&season_id={1}&mode=tv&sitemode=unwatch_episode'.format(data['title'], data['season_id'])
    #    contextmenu.append(('Mark as unwatched', 'XBMC.RunPlugin(%s)' % cm_u))
    #else:
    #    cm_u = sys.argv[0] + '?url={0}&season_id={1}&mode=tv&sitemode=watch_episode'.format(data['title'], data['season_id'])
    #    contextmenu.append(('Mark as watched', 'XBMC.RunPlugin(%s)' % cm_u))

    # contextmenu.append(('Episode Information', 'XBMC.Action(Info)'))

    cm_u = sys.argv[0] + '?url={0}&season_id={1}&mode=tv&sitemode=export_episode'.format(data['title'], data['season_id'])
    contextmenu.append(('Export Episode', 'XBMC.RunPlugin(%s)' % cm_u))

    item.addContextMenuItems(contextmenu)

    u = create_play_link(data)
    xbmcplugin.addDirectoryItem(pluginhandle, url=u, listitem=item, isFolder=False, totalItems=total)


def create_play_link(episode):
    return sys.argv[0] + '?url={0}&mode=tv&sitemode=play_episode&season_id={1}&episode_title={2}' \
        '&episode_no={3}&season_no={4}&series_title={5}'.format(
        urllib.quote_plus(episode['season_url']),
        episode['season_id'],
        urllib.quote_plus(episode['title']),
        episode['episode_no'],
        episode['season_no'],
        urllib.quote_plus(episode['series_title']))


def play_episode():
    try:
        import urlresolver
    except:
        xbmcgui.Dialog().ok("Play Error", "Failed to import URLResolver",
                            "A component needed by PFTV is missing on your system")
        xbmcplugin.setResolvedUrl(pluginhandle, False, xbmcgui.ListItem())
        return

    links = tv_db.get_media_urls(urllib.unquote_plus(common.args.url), urllib.unquote_plus(common.args.episode_title))
    sources = []
    for link in links:
        print link
        sources.append(urlresolver.HostedMediaFile(host=link['host'], media_id=link['media_id'], title=link['title']))

    source = urlresolver.choose_source(sources)

    if source:
        stream_url = source.resolve()
        xbmcplugin.setResolvedUrl(pluginhandle, True, xbmcgui.ListItem(path=stream_url))
    else:
        xbmcplugin.setResolvedUrl(pluginhandle, False, xbmcgui.ListItem())


##########################################
# Context Menu Links
##########################################
def refresh_db():
    tv_db.update_series_list(True)


def export_season():
    season_id = common.args.url
    season = tv_db.lookup_season(season_id).fetchone()
    tv_db.update_season(season)

    import xbmclibrary
    added_folders = xbmclibrary.setup_library()
    xbmclibrary.export_season(season)
    xbmclibrary.complete_export(added_folders)


def export_episode():
    episode_title = common.args.url
    season_id = common.args.season_id
    episode = tv_db.lookup_episode(episode_title, season_id)

    import xbmclibrary
    added_folders = xbmclibrary.setup_library()
    xbmclibrary.export_episode(episode)
    xbmclibrary.complete_export(added_folders)


def favor_series():
    content_id = common.args.url
    if tv_db.favor_series(content_id) > 0:
        common.notification('Added ' + urllib.unquote_plus(common.args.title) + ' to favorites')
        common.refresh_menu()
    else:
        common.notification('Error adding movie to favorites', isError=True)


def unfavor_series():
    content_id = common.args.url
    if tv_db.unfavor_series(content_id) > 0:
        common.notification('Removed ' + urllib.unquote_plus(common.args.title) + ' from favorites')
        common.refresh_menu()
    else:
        common.notification('Error removing movie from favorites', isError=True)


def update_series():
    series = tv_db.lookup_series(common.args.url).fetchone()
    tv_db.update_series(series, True)
    common.notification('{0} Updated'.format(series['title']))


def update_season():
    season = tv_db.lookup_season(common.args.url).fetchone()
    tv_db.update_season(season, True)
    common.notification('{0} Updated'.format(season['title']))


def watch_episode():
    content_id = common.args.url
    if tv_db.watch_episode(content_id) > 0:
        common.refresh_menu()
    else:
        common.notification('Could not update watch count', isError=True)


def unwatch_episode():
    content_id = common.args.url
    tv_db.unwatch_episode(content_id)
    common.refresh_menu()