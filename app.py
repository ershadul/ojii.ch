# -*- coding: utf-8 -*-
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
# Local Server
#==============================================================================

if __name__ == "__main__":
    app.run(debug=True)
