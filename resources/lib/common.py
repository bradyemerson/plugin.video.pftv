#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import urllib
from datetime import datetime
import time
import unicodedata

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


pluginHandle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon()
__addonid__ = __addon__.getAddonInfo('id')
__addonversion__ = __addon__.getAddonInfo('version')
__addonname__ = __addon__.getAddonInfo('name')
__addonpath__ = __addon__.getAddonInfo('path').decode('utf-8')
__addonprofile__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode('utf-8')
__icon__ = __addon__.getAddonInfo('icon')
__fanart__ = __addon__.getAddonInfo('fanart')

# Ensure the profile directory exists. Not sure if it's possible for it not to exist, but to be safe
if not os.path.exists(__addonprofile__):
    os.makedirs(__addonprofile__)


class _Info:
    def __init__(self, s):
        args = urllib.unquote_plus(s).split(' , ')
        for x in args:
            try:
                (k, v) = x.split('=', 1)
                setattr(self, k, v.strip('"\''))
            except:
                pass
        if not hasattr(self, 'url'):
            setattr(self, 'url', '')


args = _Info(sys.argv[2][1:].replace('&', ' , '))


# Fixes unicode problems
def string_unicode(text, encoding='utf-8'):
    try:
        text = unicode(text, encoding)
    except:
        pass
    return text


def normalize_string(text):
    try:
        text = unicodedata.normalize('NFKD', string_unicode(text)).encode('ascii', 'ignore')
    except:
        pass
    return text


def localise(id):
    string = normalize_string(__addon__.getLocalizedString(id))
    return string


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (__addonname__, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGNOTICE)


def notification(message, timer=5000, isError=False):
    icon = __icon__
    if isError:
        icon = xbmcgui.NOTIFICATION_ERROR

    dialog = xbmcgui.Dialog()
    dialog.notification(__addonname__, message, icon, timer)


def refresh_menu():
    xbmc.executebuiltin('Container.Refresh')


def get_setting(setting):
    return __addon__.getSetting(setting)


def open_settings():
    __addon__.openSettings()


def add_directory(name, mode='', sitemode='', directory_url='', thumb=None, fanart=None, description=None,
                  contextmenu=None, is_folder=True):
    if fanart is None:
        if args.__dict__.has_key('fanart'):
            fanart = args.fanart
        else:
            fanart = __fanart__
    if thumb is None:
        if args.__dict__.has_key('poster'):
            thumb = args.poster
        elif args.__dict__.has_key('thumb'):
            thumb = args.thumb
        else:
            thumb = ''
    infoLabels = {'title': name,
                  'plot': description}
    u = sys.argv[0]
    u += '?url="' + urllib.quote_plus(directory_url) + '"'
    u += '&mode="' + mode + '"'
    u += '&sitemode="' + sitemode + '"'
    u += '&thumb="' + urllib.quote_plus(thumb) + '"'
    u += '&fanart="' + urllib.quote_plus(fanart) + '"'
    u += '&name="' + urllib.quote_plus(name) + '"'
    item = xbmcgui.ListItem(name, iconImage=thumb, thumbnailImage=thumb)
    item.setProperty('fanart_image', fanart)
    item.setInfo(type='Video', infoLabels=infoLabels)

    if contextmenu:
        item.addContextMenuItems(contextmenu)

    xbmcplugin.addDirectoryItem(pluginHandle, url=u, listitem=item, isFolder=is_folder)


def parse_date(date, format='%Y-%m-%d'):
    # http://forum.kodi.tv/showthread.php?tid=112916
    try:
        return datetime.strptime(date, format)
    except TypeError:
        return datetime(*(time.strptime(date, format)[0:6]))
