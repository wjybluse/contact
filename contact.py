# -*- coding: utf-8 -*-
__author__ = 'wan'
import os
import json
import time
import logging

from flask import Flask, render_template_string
from flask import render_template
from flask import request, session, flash
from werkzeug.utils import secure_filename

from orm.dbserver import DBServer
from orm.user import User
from orm.message import Message
from tools.conf import general_uid
from gevent.queue import Queue
from flask import Response

UPLOAD = 'static/upload/'

# global varibale
chat_room = {}
message_queue = {}
# init app
app = Flask(__name__)
app.secret_key = '0418fa7f-ec29-40a8-84e1-e4d6c597fbd2'

# init database
db = DBServer(os.path.join(app.root_path, 'conf/db-config.cfg'), 'contact_user')
message = DBServer(os.path.join(app.root_path, 'conf/db-config.cfg'), 'contact_message')

# init log handler
logger = app.logger
file_handler = logging.FileHandler(os.path.join(app.root_path, 'log/flask.log'))
file_handler.setLevel(logging.DEBUG)
logger.addHandler(file_handler)

# init socket io


# traditional method
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
@app.errorhandler(401)
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if is_login(session):
        user = User.find_user(db, _user=request.form['_user'])
        if getattr(user, 'path', None) is not None:
            return render_template('user.html', user=user)
        flash('Sign up ok!Please compelete your infromation', 'warning')
        return render_template('profile.html', user=user)
    user = validate_user(request.form['_user'], request.form['_password'])
    if user is None:
        flash("Invalid username/password or the user does not exist", 'error')
        return render_template('login.html')
    session['_user'] = user.uid
    if getattr(user, 'path', None) is None:
        return render_template('profile.html', user=user)
    return render_template('user.html', user=user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    uid = str(general_uid())
    try:
        db.insert(uid=[uid], datetime=[time.time()], **request.form)
    except ValueError, e:
        logger.error("error message %s", str(e))
        flash("The phone was sign up,please sign in or find the password", 'error')
        return render_template('login.html')
    user = User.covert(uid=[uid], **request.form)
    session['_user'] = uid
    flash('Sign up ok ! Please complete your information', 'warning')
    return render_template('profile.html', user=user)


@app.route('/profile/<uid>', methods=['GET', 'POST'])
@app.errorhandler(500)
def profile_handler(uid=None):
    if not is_login(session):
        return render_template('login.html')
    if request.method == 'GET':
        user = User.find_user(db, uid=uid)
        if is_current_user(session['_user'], uid):
            logger.debug('current user %s,uid user %s', session['_user'], uid)
            if user.path is None:
                return render_template('profile.html', user=user)
            logger.info("Find the user %s", user.__dict__)
            return render_template('user.html', user=user)
        return render_template('_profile.html', user=user)
    f = request.files['file']
    fn = secure_filename(f.filename)
    if not os.path.exists(os.path.join(UPLOAD, uid)):
        os.makedirs(os.path.join(UPLOAD, uid))
    p = os.path.join(os.path.join(UPLOAD, uid), fn)
    f.save(p)
    db.update({'uid': uid}, path=p, _company=request.form['_company'], _address=request.form['_address'])
    return render_template('user.html', user=User.find_user(db, uid=uid))


@app.route('/user')
@app.route('/user/<uid>')
def user_handler(uid=None):
    if not is_login(session):
        flash('Please log in before', 'error')
        return render_template('login.html')
    if uid is None or len(uid) <= 0:
        uid = session['_user']
    user = User.find_user(db, uid=uid)
    if is_current_user(session['_user'], uid):
        return render_template('user.html', user=user)
    return render_template('_profile.html', user=user)


@app.errorhandler(401)
def validate_user(username, password):
    user = find_user(username, password)
    if user is None:
        logger.error("Invalid username %s or %s password", username, password)
        return None
    logger.info("find the user %s %s", username, password)
    return user


@app.route('/person/<cls>')
@app.errorhandler(400)
def person_handler(cls=None):
    if not is_login(session):
        flash('Please log in and see', 'error')
        return render_template('login.html')
    if cls is None:
        flash('The class id invalid', 'error')
        return render_template('_400.html')
    users = User.find_by_condition(db, _class=cls)
    return render_template('person.html', users=users)


@app.route('/message')
@app.route('/message/<uid>', methods=['GET', 'POST', 'DELETE'])
def message_handler(uid=None):
    if not is_login(session):
        return render_template('login.html')
    if request.method == 'GET':
        if uid is None:
            return render_template_string(json.dumps(Message.find_all_message(message)))
        return render_template_string(json.dumps(Message.find_message(message, uid=uid)))
    if request.method == 'POST':
        text = request.form['tweet']
        _message_id = request.form['_message']
        data = dict(tweet=[text], uid=[uid], _message=[_message_id], datetime=[time.time()])
        message.insert(**data)
        return "ok"
    if request.method == 'DELETE':
        message.remove(_message=uid)
        return "ok"
    return render_template('_404.html')


@app.route('/logout', methods=['DELETE'])
def logout():
    if '_user' in session:
        session.pop('_user')
    return render_template('login.html')


# server send event
@app.route('/chat_room/<room>/<user>', methods=['GET', 'POST', 'DELETE'])
@app.error_handlers(500)
def chat_room(room=None, user=None):
    if request.method == 'DELETE':
        remove_from_room(user, room)
        return Response(user + " exit!", mimetype="text/event-stream")
    if request.method == 'GET':
        if room is None or user is None:
            raise ValueError("room id can not be empty")
        flush_room(user, room)
        return Response(user + " has entered!", mimetype="text/event-stream")
    data = request.form['data']
    if request.form['data'] is None:
        raise ValueError("Can not support empty message")
    return Response(data, mimetype="text/event-stream")


@app.route('/destroy/<room>')
def destroy_room(room=None):
    if room is None:
        return ""
    if room in chat_room:
        chat_room.pop(room)
        return "Destroy the chat room!"
    return ""


def remove_from_room(user, room):
    if room in chat_room:
        chat_room[room].peek(user)


def flush_room(user, room):
    if room not in chat_room:
        chat_room[room] = Queue()
        chat_room[room].put(user)
    else:
        if not chat_room[room].get(user):
            chat_room[room].put(user)


def find_user(username, password):
    user = User.find_user(db, _user=username, _password=password)
    return user


def is_login(session):
    return '_user' in session


def is_current_user(session_user, uid_user):
    return session_user == uid_user


if __name__ == '__main__':
    app.run()
