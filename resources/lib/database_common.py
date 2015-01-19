#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import urllib
import re

import common

WEB_DOMAIN = 'http://www.free-tv-video-online.me'

def re_fn(expr, item):
    reg = re.compile(expr, re.I)
    return reg.search(item) is not None