# -*- coding: utf-8 -*-
# Copyright (c) 2012, Jonas Obrist
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Jonas Obrist nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL JONAS OBRIST BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
