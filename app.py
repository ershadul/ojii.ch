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
from flask import Flask, render_template
from raven.contrib.flask import Sentry
from timeline import gather
from timesince import timesince
from twitterlink import autolink
from werkzeug.contrib.cache import MemcachedCache
import os
import pylibmc

#==============================================================================
# Configuration
#==============================================================================

CACHE_TIMEOUT = 5 * 60

#==============================================================================
# App Setup
#==============================================================================

app = Flask(__name__)

app.template_filter('twitterlink')(autolink)
app.template_filter('timesince')(timesince)

#==============================================================================
# Error Logging
#==============================================================================

SENTRY_DSN = os.environ.get('SENTRY_DSN', None)
if SENTRY_DSN:
    app.config['SENTRY_DSN'] = SENTRY_DSN
    sentry = Sentry(app)

#==============================================================================
# Caching
#==============================================================================

memcache_client = pylibmc.Client(
    servers=[os.environ.get('MEMCACHE_SERVERS', '127.0.0.1:11211')],
    username=os.environ.get('MEMCACHE_USERNAME', None),
    password=os.environ.get('MEMCACHE_PASSWORD', None),
    binary=True
)

cache = MemcachedCache(memcache_client)

def gather_cached():
    key = 'ojii.ch:gather_cached'
    cached = cache.get(key)
    if cached:
        return cached
    else:
        uncached = gather()
        cache.set(key, uncached, CACHE_TIMEOUT)
        return uncached

#==============================================================================
# Views
#==============================================================================

@app.route("/")
def hello():
    return render_template('index.html', messages=gather_cached())

@app.route("/meta/")
def meta():
    return render_template('meta.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#==============================================================================
# Server
#==============================================================================

if __name__ == "__main__":
    port = os.environ.get("PORT", None)
    if port is None:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=int(port))
