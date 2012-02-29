# -*- coding: utf-8 -*-
import re

TWITTER_USER_RE = re.compile(r'@(\w+)(\s|$)')
SIMPLE_LINK_REGEX = re.compile(r'http://')


def autolink(message):
    return TWITTER_USER_RE.sub(r'<a href="https://twitter.com/\1">@\1</a>\2', message)
