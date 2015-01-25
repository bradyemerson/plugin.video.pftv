#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2

import common


TIMEOUT = 50


def get_url(url, header={}):
    try:
        common.log('connection :: getURL :: url = ' + url)
        req = urllib2.Request(bytes(url))
        header.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/39.0.2171.95 Safari/537.36'})
        for key, value in header.iteritems():
            req.add_header(key, value)
        response = urllib2.urlopen(req, timeout=TIMEOUT)
        link = response.read()
        response.close()
    except urllib2.HTTPError, error:
        print 'HTTP Error reason: ', error
        return False
    else:
        return link

