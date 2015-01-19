#!/usr/bin/python
# -*- coding: utf-8 -*-
import resources.lib.common as common
import resources.lib.listmovie as listmovie
import resources.lib.listtv as listtv
import os
import sys
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui

pluginHandle = int(sys.argv[1])

__plugin__ = 'Project Free TV'
__authors__ = 'bemerson'
__credits__ = 'moneymaker, slices, zero'
__version__ = '0.0.1'

def modes():
    if sys.argv[2] == '':

        cm = [('Force Movie Database Refresh', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=movies&sitemode=refresh_db'))]
        #common.add_directory('Movies', 'movies', 'list_movie_root', contextmenu=cm)

        cm = [('Force TV Series Refresh', 'XBMC.RunPlugin(%s)' % (sys.argv[0] + '?mode=tv&sitemode=refresh_db'))]
        common.add_directory('TV Shows', 'tv', 'list_tv_root', contextmenu=cm)

        common.add_directory('Video Resolver Settings', 'n/a', 'resolver_settings', is_folder=False)

        xbmcplugin.addSortMethod(pluginHandle, xbmcplugin.SORT_METHOD_PLAYLIST_ORDER)
        xbmcplugin.endOfDirectory(pluginHandle)

    elif common.args.mode == 'movies':
        getattr(listmovie, common.args.sitemode)()
    elif common.args.mode == 'tv':
        getattr(listtv, common.args.sitemode)()
    else:
        if common.args.sitemode == 'resolver_settings':
            try:
                import urlresolver
                urlresolver.display_settings()
            except:
                xbmcgui.Dialog().ok("Play Error", "Failed to import URLResolver", "A component needed by PFTV is missing on your system")

modes()
sys.modules.clear()