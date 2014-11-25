import os
from flask import Flask
from flask import render_template
from flask import request, make_response, session, flash, redirect
from orm.dbserver import DBServer
from orm.user import User
from tools.conf import general_uid
from werkzeug.utils import secure_filename
from domain.validate import Validate

app = Flask(__name__)
app.debug = True
app.secret_key = '0418fa7f-ec29-40a8-84e1-e4d6c597fbd2'
db = DBServer(os.path.join(app.root_path, 'conf/db-config.cfg'))
logger = app.logger
UPLOAD = 'static/upload/'
validate = Validate(db, session)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
@app.errorhandler(401)
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if '_user' in session:
        return render_template('profile.html', user=User.find_user(db, _user=request.form['_user']))
    user = validate_user(request.form['_user'], request.form['_password'])
    if user is None:
        flash("Invalid username/password or the user does not exist", 'error')
        return render_template('signup.html')
    user = User.covert(**user)
    session['_user'] = user.id
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


@app.route('/profile/<phone>', methods=['GET', 'POST'])
@app.errorhandler(500)
def profile(phone=None):
    if not validate.is_login():
        return render_template('login.html')
    if request.method == 'GET':
        user = User.find_user(db, phone=phone)
        logger.info("Find the user %s", user.__dict__)
        return render_template('profile.html', user=user)
    f = request.files['file']
    fn = secure_filename(f.filename)
    os.makedirs(os.path.join(UPLOAD, phone))
    p = os.path.join(os.path.join(UPLOAD, phone), fn)
    f.save(p)
    db.update({'phone': phone}, path=p, **covert_data())
    return render_template('user.html', user=User.find_user(db, phone=phone))


def covert_data():
    data = dict()
    for k, val in request.form.items():
        if 'file' or 'submit' in k:
            continue
        data[str(k)] = val[0]
    return data


@app.errorhandler(401)
def validate_user(username, password):
    user = find_user(username, password)
    if user is None or len(user) <= 0:
        logger.error("Invalid username {0} or {1} password", username, password)
        return None
    logger.info("find the user %s %s", username, password)
    return user[0]


@app.route('/person/<cls>')
@app.errorhandler(400)
def person(cls=None):
    if not validate.is_login():
        return render_template('login.html')
    if cls is None:
        raise "Invalid request"
    users = User.find_user(db, _class=cls)
    return render_template('person.html', users)


@app.route('/logout/<user>', methods=['DELETE'])
def logout():
    session.pop('_user')
    return render_template('login.html')


def find_user(username, password):
    user = db.query(_user=username, _password=password)
    return user


if __name__ == '__main__':
    app.run()
