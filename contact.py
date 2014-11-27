import os
from flask import Flask
from flask import render_template
from flask import request, make_response, session, flash, redirect
from orm.dbserver import DBServer
from orm.user import User
from orm.message import Message
from tools.conf import general_uid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.debug = True
app.secret_key = '0418fa7f-ec29-40a8-84e1-e4d6c597fbd2'
db = DBServer(os.path.join(app.root_path, 'conf/db-config.cfg'), 'contact_user')
message = DBServer(os.path.join(app.root_path, 'conf/db-config.cfg'), 'contact_message')
logger = app.logger
UPLOAD = 'static/upload/'


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
@app.errorhandler(401)
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if is_login():
        return render_template('profile.html', user=User.find_user(db, _user=request.form['_user']))
    user = validate_user(request.form['_user'], request.form['_password'])
    if user is None:
        flash("Invalid username/password or the user does not exist", 'error')
        return render_template('signup.html')
    session['_user'] = user.uid
    if user.path is not None:
        return render_template('user.html', user=user)
    return render_template('profile.html', user=user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')
    uid = str(general_uid())
    try:
        db.insert(uid=[uid], **request.form)
    except ValueError, e:
        logger.error("error message %s", str(e))
        flash("The phone was sign up,please sign in or find the password", 'error')
        return render_template('login.html')
    user = User.covert(uid=[uid], **request.form)
    session['_user'] = uid
    return render_template('profile.html', user=user)


@app.route('/profile/<uid>', methods=['GET', 'POST'])
@app.errorhandler(500)
def profile(uid=None):
    if not is_login():
        return render_template('login.html')
    if request.method == 'GET':
        user = User.find_user(db, uid=uid)
        logger.info("Find the user %s", user.__dict__)
        return render_template('profile.html', user=user)
    f = request.files['file']
    fn = secure_filename(f.filename)
    if not os.path.exists(os.path.join(UPLOAD, uid)):
        os.makedirs(os.path.join(UPLOAD, uid))
    p = os.path.join(os.path.join(UPLOAD, uid), fn)
    f.save(p)
    db.update({'uid': uid}, path=p, **covert_data())
    return render_template('user.html', user=User.find_user(db, uid=uid))


@app.route('/user')
@app.route('/user/<uid>')
def hand_user(uid=None):
    if not is_login():
        flash('Please log in before', 'error')
        return render_template('login.html')
    if uid is None or len(uid) <= 0:
        uid = session['_user']
    return render_template('user.html', user=User.find_user(db, uid=uid))


def covert_data():
    data = dict()
    for k, val in request.form.items():
        # filter the file and submit
        if 'file' or 'submit' in k:
            continue
        data[str(k)] = val[0]
    return data


@app.errorhandler(401)
def validate_user(username, password):
    user = find_user(username, password)
    if user is None:
        logger.error("Invalid username {0} or {1} password", username, password)
        return None
    logger.info("find the user %s %s", username, password)
    return user


@app.route('/person/<cls>')
@app.errorhandler(400)
def person(cls=None):
    if not is_login():
        flash('Please log in and see', 'error')
        return render_template('login.html')
    if cls is None:
        flash('The class id invalid', 'error')
        return render_template('_400.html')
    users = User.find_user(db, _class=cls)
    return render_template('person.html', users)


@app.route('/message')
@app.route('/message/<uid>', methods=['GET', 'POST'])
def message_handler(uid=None):
    if not is_login():
        return render_template('login.html')
    if request.method == 'GET':
        if uid is None:
            return Message.find_all_message(message)
        return Message.find_all_message(message, uid=uid)
    if request.method == 'POST':
        text = request.form['tweet']
        data = dict(tweet=text, uid=uid)
        message.insert(**data)
        return "ok"
    return render_template('_404.html')


@app.route('/logout', methods=['DELETE'])
def logout():
    session.pop('_user')
    return render_template('login.html')


def find_user(username, password):
    user = User.find_user(db, _user=username, _password=password)
    return user


def is_login():
    return '_user' in session


if __name__ == '__main__':
    app.run()
