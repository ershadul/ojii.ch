# -*- coding: utf-8 -*-
from werkzeug.contrib.cache import MemcachedCache
import datetime
import json
import requests
import time
import rfc822


CACHE_KEY_TEMPLATE = 'ojii.ch:timeline:%s'
CACHE_TIMEOUT = 5 * 60

cache = MemcachedCache(['127.0.0.1:11211'])

def cached(func):
    key = CACHE_KEY_TEMPLATE % func.__name__
    cached = cache.get(key)
    if cached:
        for thing in cached:
            yield thing
    else:
        items = []
        for thing in func():
            yield thing
            items.append(thing)
        cache.set(key, items, timeout=CACHE_TIMEOUT)


GITHUB_URL = 'https://api.github.com/users/ojii/events'
GITHUB_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ' # 2012-02-28T14:34:28Z
GITHUB_EVENTS = ['WatchEvent', 'PushEvent', 'IssuesEvent', 'IssueCommentEvent',
                 'PullRequestEvent', 'CommitCommentEvent']

def github():
    response = requests.get(GITHUB_URL)
    if not response.ok:
        raise StopIteration()
    for obj in json.loads(response.content):
        if obj['type'] in GITHUB_EVENTS:
            obj['timestamp'] = time.mktime(datetime.datetime.strptime(obj['created_at'], GITHUB_TIME_FORMAT).timetuple())
            obj['template'] = 'github/%s.html' % obj['type'].lower()
            yield obj

TWITTER_URL = 'https://search.twitter.com/search.json?q=from:ojiidotch'

def twitter():
    response = requests.get(TWITTER_URL)
    if not response.ok:
        raise StopIteration()
    for obj in json.loads(response.content)['results']:
        obj['timestamp'] = time.mktime(rfc822.parsedate_tz(obj['created_at'])[:-1])
        obj['template'] = 'twitter/tweet.html'
        yield obj

def internal():
    return []

def gather():
    items = []
    items.extend(cached(github))
    items.extend(cached(twitter))
    items.extend(cached(internal))
    return sorted(items, key=lambda item: -item['timestamp'])
