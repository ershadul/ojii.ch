# -*- coding: utf-8 -*-
import datetime
import json
import requests
import time
import rfc822

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
    items.extend(github())
    items.extend(twitter())
    items.extend(internal())
    return sorted(items, key=lambda item: -item['timestamp'])
