# coding:utf-8
from flask import Flask, session
from datetime import timedelta
import os
import pymysql

db = pymysql.connect(database="localhost", user='root', password='123456', charset='utf8mb4')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)

print("the name is: " + __name__)


@app.route('/')
def hello_world():
    session['username'] = 'saber'
    # session permanent 持久化置为True则session课保存31天.
    session.permanent = True
    return 'Hello World!'


@app.route('/get_session/')
def get_session():
    username = session.get('username')
    return username or u'no session set'


@app.route('/delete_session/')
def delete_session():
    # clear session 'username'
    session.pop('username')
    # clear all session.
    session.clear()
    return 'delete success.'


if __name__ == '__main__':
    app.run(debug=True)
