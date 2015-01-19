#!/usr/bin/python
# -*- coding: utf-8 -*-
import cookielib
import os
import urllib
import urllib2

import common


RESOURCESPATH = os.path.join(common.__addonpath__, 'resources')
CACHEPATH = os.path.join(common.__addonpath__, 'cache')
COOKIE = os.path.join(common.__addonpath__, 'cookie.txt')
TIMEOUT = 50


def get_url(url, values=None, header={}, amf=False, savecookie=False, loadcookie=False, cookiefile=None):
    try:
        old_opener = urllib2._opener
        cj = cookielib.LWPCookieJar(COOKIE)
        cookie_handler = urllib2.HTTPCookieProcessor(cj)
        urllib2.install_opener(urllib2.build_opener(cookie_handler))

        print '_connection :: getURL :: url = ' + url
        if values is None:
            req = urllib2.Request(bytes(url))
        else:
            if amf == False:
                data = urllib.urlencode(values)
            elif amf == True:
                data = values
            req = urllib2.Request(bytes(url), data)
        header.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'})
        for key, value in header.iteritems():
            req.add_header(key, value)
        if loadcookie is True:
            try:
                cj.load(ignore_discard=True)
                cj.add_cookie_header(req)
            except:
                print 'Cookie Loading Error'
                pass
        response = urllib2.urlopen(req, timeout=TIMEOUT)
        link = response.read()
        if savecookie is True:
            try:
                cj.save(ignore_discard=True)
            except:
                print 'Cookie Saving Error'
                pass
        response.close()
        urllib2.install_opener(old_opener)
    except urllib2.HTTPError, error:
        print 'HTTP Error reason: ', error
        return False
    else:
        return link

