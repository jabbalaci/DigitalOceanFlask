#!/usr/bin/env python3
# encoding: utf-8

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

##############################################################################

if __name__ == '__main__':
    print("# app.run() is called, you must be using Flask's dev server")
    print("# Warning! You are in development mode => debug is ON!")
    app.run(debug=True, host='0.0.0.0', port=9000)
else:
    print("# app.run() is NOT called, you must be using Gunicorn")
    print("# Production mode, debug is OFF.")
