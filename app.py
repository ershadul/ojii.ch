# -*- coding: utf-8 -*-
from flask import Flask, render_template
from timeline import gather
from timesince import timesince

DEFAULT_TIME_FORMAT = ''

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html', messages=gather())

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.template_filter('timesince')(timesince)

if __name__ == "__main__":
    app.run(debug=True)
