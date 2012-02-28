# -*- coding: utf-8 -*-
from flask import Flask, render_template
from timeline import gather
from timesince import timesince

DEFAULT_TIME_FORMAT = ''

app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html', messages=gather())

app.template_filter('timesince')(timesince)

if __name__ == "__main__":
    app.run(debug=True)
