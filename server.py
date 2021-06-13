import re

from flask import Flask, render_template, request, session, redirect, url_for, jsonify, escape
import pymysql
import os
import bcrypt
from datetime import datetime
from flask_socketio import SocketIO, emit, join_room, leave_room, send
import base64
from PIL import Image
import json

db = pymysql.connect(host='db', user='root', password=os.getenv(
    'MYSQL_PASSWORD'), db='zhong', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)

# db = pymysql.connect(host='localhost', user='root', password='sze111', charset='utf8mb4',
#                    cursorclass=pymysql.cursors.DictCursor)

cur = db.cursor()
cur.execute("create database IF NOT EXISTS zhong")
cur.execute("use zhong")
cur.execute(
    "create table IF NOT EXISTS user(username varchar(200), email varchar(50), password varchar(500),icon varchar("
    "200) default 'fakeuser.png', gender varchar(10), birth varchar(20), personal_page varchar(100), introduction "
    "varchar(500));")
cur.execute(
    "create table IF NOT EXISTS blog(filename varchar(200), filetype varchar(50), "
    "comment varchar(500), username varchar(200), date varchar(20));")
cur.execute(
    "create table IF NOT EXISTS message(sender varchar(50), receiver varchar(50),"
    "message varchar(500), date varchar(20));")
cur.execute("alter table user convert to character set utf8mb4 collate utf8mb4_bin;")
cur.execute("alter table blog convert to character set utf8mb4 collate utf8mb4_bin;")
cur.execute("alter table message convert to character set utf8mb4 collate utf8mb4_bin;")
db.commit()

app = Flask(__name__)
app.secret_key = os.urandom(50)
socketio = SocketIO(app)

online_users = []
users_icon = dict()
game_users = []


@app.before_request
def advance_session_timeout():
    session.permanent = False


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@app.route('/index.html', methods=['POST', 'GET'])
def hello_world():
    if 'user' in session:
        username = session['user']
    else:
        username = None
    sql = "select * from blog order by date desc"
    cur.execute(sql)
    blogs = cur.fetchall()

    online_users.sort()
    users_login = list()
    for user in online_users:
        temp = dict()
        temp['username'] = user
        temp['icon'] = users_icon[user]
        users_login.append(temp)

    if users_login:
        return render_template('index.html', user=username, blogs=blogs, users=users_login)
    else:
        return render_template('index.html', user=username, blogs=blogs)


@socketio.on('connect')
def connect_handler():
    if 'user' in session:
        room = session['user']
        join_room(room)
        if session['user'] not in online_users:
            online_users.append(session['user'])
            sql = "select username, icon from user where username=(%s)"
            cur.execute(sql, (session['user'],))
            user = cur.fetchone()
            emit('new_user', user, broadcast=True)
            if room in game_users:
                emit('new_gamer', room, broadcast=True)


@socketio.on('disconnect')
def disconnect_handler():
    if 'user' in session:
        room = session['user']
        leave_room(room)
        if room in game_users:
            game_users.remove(room)
            for user in game_users:
                send(game_users, room=user)
        online_users.remove(room)
        online_users.sort()
        users_login = list()
        for user in online_users:
            temp = dict()
            temp['username'] = user
            temp['icon'] = users_icon[user]
            users_login.append(temp)
        if users_login:
            # We convert the a list to JSON data
            # https://www.w3schools.com/python/python_json.asp
            users_json = json.dumps(users_login)
            send(users_json, json=True, broadcast=True)
        else:
            send(json.dumps(""), json=True, broadcast=True)


@socketio.on('send-message')
def display(message):
    if 'user' in session:
        username = session['user']
    else:
        username = None
    comment = message['comment']
    file_name = ''
    file_type = ''
    if 'file' in message.keys():
        file_name = message['filename']
        file_type = message['filetype']
        file = message['file']
        file_index = file.find('base64,')
        file_byte = base64.b64decode(file[file_index + len('base64,'):])

        with open("static/images/" + file_name, "wb") as file2:
            file2.write(file_byte)
            file2.close()

    now = datetime.now()
    date = now.strftime("%m/%d/%Y %H:%M:%S")

    sql = "insert into blog values (%s,%s,%s,%s,%s)"
    cur.execute(sql, (file_name, file_type, comment, username, date))
    db.commit()

    comment = escape(comment)

    emit('blog_done',
         {'user': username, 'date': date, 'comment': comment, 'filename': file_name, 'filetype': file_type},
         broadcast=True)


@app.route('/about.html')
def about():
    if 'user' in session:
        return render_template('about.html', user=session['user'])
    return render_template('about.html')


@app.route('/login.html', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 一些判断语句验证，1：用户名是否存在 2：密码是否正确
        sql = "select * from user where username = (%s)"
        cur.execute(sql, (username,))
        name = cur.fetchone()
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
        rd_suc = '<script>setTimeout(function(){window.location.href="/index.html";}, 3000);</script>'
        if name is None:
            return "<h1>This username does not exist!</h1>" + redirecting + rd_fail

        if bcrypt.checkpw(password.encode(), name['password'].encode()):
            if username in online_users:
                return "<h1>This account is already logged in. </h1>" + redirecting + rd_fail
            session['user'] = username
            users_icon[username] = name['icon']
            return "<h1>Welcome back：" + username + "</h1>" + redirecting + rd_suc
        else:
            return "<h1>Failed. The username: " + username + " or password incorrect.</h1>" + redirecting + rd_fail
    if 'user' in session:
        # Use the combination of redirect and url_for functions to redirect to other page
        # https://flask.palletsprojects.com/en/1.1.x/quickstart/
        return redirect(url_for('profile'))
    else:
        return render_template('login.html')


@app.route('/reset.html', methods=['POST', 'GET'])
def reset():
    if request.method == 'POST':
        username = request.form['username']
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        cnew_password = request.form['cnew_password']
        sql = "select * from user where username = (%s)"
        cur.execute(sql, (username,))
        name = cur.fetchone()
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/reset.html";}, 3000);</script>'
        rd_suc = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
        if name is None:
            return "<h1>This username does not exist!</h1>" + redirecting + rd_fail
        if new_password != cnew_password:
            return "<h1>The new passwords are not same!</h1>" + redirecting + rd_fail
        regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$"
        pattern = re.compile(regex)
        validation = re.search(pattern, new_password)
        if not validation:
            return "<h1>Password requirements are not satisfied</h1>" + redirecting + rd_fail

        if bcrypt.checkpw(old_password.encode(), name['password'].encode()):
            salt = bcrypt.gensalt()
            h = new_password.encode()
            hashed = bcrypt.hashpw(h, salt)
            cur.execute("UPDATE user SET password=%s WHERE username=%s", (hashed, username))
            db.commit()
            session.pop('user', None)
            return "<h1>The password is changed. Please login again.</h1>" + redirecting + rd_suc
        else:
            return "<h1>The old password is incorrect. Please try again.</h1>" + redirecting + rd_fail

    if 'user' in session:
        return render_template('reset.html', user=session['user'])
    else:
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
        return "<h1>Please login first.</h1>" + redirecting + rd_fail


@app.route('/forgot.html', methods=['POST', 'GET'])
def forgot():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # 一些判断语句验证，1：用户名是否存在 2：密码是否正确
        sql = "select * from user where username = (%s)"
        cur.execute(sql, (username,))
        name = cur.fetchone()
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/forgot.html";}, 3000);</script>'
        rd_suc = '<script>setTimeout(function(){window.location.href="/login.html";}, 5000);</script>'
        if name is None:
            return "<h1>This username does not exist!</h1>" + redirecting + rd_fail

        if name['email'] == email:
            newpassword = 'abcd1234'
            salt = bcrypt.gensalt()
            h = newpassword.encode()
            hashed = bcrypt.hashpw(h, salt)
            cur.execute("UPDATE user SET password=%s WHERE username=%s", (hashed, username))
            db.commit()
            return "<h1>Hello, " + username + ", your new password is <span style='color:blue'>" + newpassword + \
                   "</span>. This password is not secure, please change it immediately.</h1>" + redirecting + rd_suc
        else:
            return "<h1>Either username or email is incorrect.</h1>" + redirecting + rd_fail

    return render_template('forgot.html')


@app.route('/logout')
def logout():
    if 'user' in session:
        if session['user'] in online_users:
            online_users.remove(session['user'])
        session.pop('user', None)
    redirecting = '<h3>Redirecting ... </h3>'
    rd_suc = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
    return "<h1>You have logout successfully.</h1>" + redirecting + rd_suc


@app.route('/register.html', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_check = request.form['pcheck']

        # 一些判断语句，比如输入空白提示，2次密码不同提示，用户名重复提示等等
        sql = "select * from user where username = (%s)"
        cur.execute(sql, (username,))
        name = cur.fetchone()
        ex = 0
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/register.html";}, 3000);</script>'
        rd_suc = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
        rd_suc2 = '<script>setTimeout(function(){window.location.href="/index.html";}, 3000);</script>'
        if name is None:
            ex = 1
        if password != password_check:
            return "<h1>Fail to register，two passwords don't match.</h1>" + redirecting + rd_fail
        elif ex == 0:
            return "<h1>Fail to register，username \"" + username + "\" existed.</h1>" + redirecting + rd_fail

        regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@.$!%*#?&])[A-Za-z\d@.$!#%*?&]{8,20}$"
        pattern = re.compile(regex)
        validation = re.search(pattern, password)
        if not validation:
            return "<h1>Password requirements are not satisfied.</h1>" + redirecting + rd_fail

        # 新用户添加到database
        salt = bcrypt.gensalt()
        h = password.encode()
        hashed = bcrypt.hashpw(h, salt)
        sql = "insert into user(username,email,password) values (%s,%s,%s)"
        cur.execute(sql, (username, email, hashed))
        db.commit()

        if 'user' in session:
            return "<h1>Register successfully, new username: " + username + ".</h1>" + redirecting + rd_suc2
        else:
            return "<h1>Register successfully, new username: " + username + ".</h1>" + redirecting + rd_suc
    if 'user' in session:
        return render_template('register.html', user=session['user'])
    return render_template('register.html')


@app.route('/profile', methods=['POST', 'GET'])
@app.route('/profile.html', methods=['POST', 'GET'])
def profile():
    if request.method == "POST":
        email = request.form['email']
        gender = request.form['gender']
        birth = request.form['birth']
        pp = request.form['personal_page']
        introduction = request.form['introduction']

        # Read the bytes of the image from input file and store it locally
        # Since the image may be very large, but the user icon does not need to be that big
        # So we store use Image method from PIL library to reduce the size of image
        # https://pillow.readthedocs.io/en/stable/reference/Image.html
        icon = request.files['icon']
        ic = icon.read()
        path = "static/images/" + icon.filename
        fout = open(path, 'wb')
        fout.write(ic)
        fout.close()
        img = Image.open(path)
        img.thumbnail((400, 400))
        icon_name = 'icon_' + icon.filename
        img.save("static/images/" + icon_name)
        # os.remove(path)

        sql = "update user set email=%s,icon=%s,gender=%s,birth=%s,personal_page=%s,introduction=%s where username=%s"
        cur.execute(sql, (email, icon_name, gender, birth, pp, introduction, session['user']))
        db.commit()
        users_icon[session['user']] = icon_name

        redirecting = '<h3>Redirecting ... </h3>'
        rd_suc = '<script>setTimeout(function(){window.location.href="/profile.html";}, 3000);</script>'

        return "<h1>You have updated your profile successfully.</h1>" + redirecting + rd_suc

    if 'user' in session:
        username = session['user']
        sql = "select * from user where username = (%s)"
        cur.execute(sql, (username,))
        user = cur.fetchone()
        gender = ""
        if user['gender']:
            gender = user['gender']

        if gender == "Male":
            return render_template('profile.html', user=user, check_male='checked')
        elif gender == "Female":
            return render_template('profile.html', user=user, check_female='checked')
        elif gender == "N/A":
            return render_template('profile.html', user=user, check_NA='checked')
        return render_template('profile.html', user=user)

    else:
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
        return "<h1>Please login first.</h1>" + redirecting + rd_fail


@app.route('/direct_chat/<send_to_user>')
def directChat(send_to_user):
    if 'user' in session:
        if session['user'] == send_to_user:
            # Use the combination of redirect and url_for functions to redirect to other page
            # https://flask.palletsprojects.com/en/1.1.x/quickstart/
            return redirect(url_for("profile"))

        sender = session['user']
        sql = "select * from message where (sender=%s and receiver=%s) or (sender=%s and receiver=%s);"
        cur.execute(sql, (sender, send_to_user, send_to_user, sender))
        messages = cur.fetchall()

        return render_template("direct_chat.html", sender=sender, send_to=send_to_user, messages=messages)
    else:
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
        return "<h1>Please login first.</h1>" + redirecting + rd_fail


@socketio.on('message')
def handleMessage(msg):
    if 'user' in session:
        sender = msg.get('sender')
        receiver = msg.get('receiver')
        message = msg.get('message')
        now = datetime.now()
        date = now.strftime("%m/%d/%Y %H:%M:%S")
        sql = "insert into message values (%s,%s,%s,%s);"
        cur.execute(sql, (sender, receiver, message, date))
        db.commit()
        # use escape() to make the message safe
        # https://flask.palletsprojects.com/en/1.1.x/quickstart/
        emit('privateMessage', {'sender': sender, 'receiver': receiver,
                                'message': escape(message), 'date': date}, room=receiver)


@app.route('/user_profile/<look_user>')
def userProfile(look_user):
    sql = "select * from user where username = (%s)"
    cur.execute(sql, (look_user,))
    look_user1 = cur.fetchone()
    if look_user1 is None:
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/index.html";}, 3000);</script>'
        return "<h1>This username does not exist.</h1>" + redirecting + rd_fail
    if 'user' in session:
        user = session['user']
        if user == look_user:
            # Use the combination of redirect and url_for functions to redirect to other page
            # https://flask.palletsprojects.com/en/1.1.x/quickstart/
            return redirect(url_for('profile'))
        return render_template("user_profile.html", user=user, look_user=look_user1)
    else:
        return render_template("user_profile.html", look_user=look_user1)


@app.route('/username_validation/')
def check_user_exist():
    result = {"exists": bool, "display": ""}
    username = request.args.get("username")
    if len(username) == 0:
        result["exists"] = True
        result["display"] = "<font color='red'> ❌ Empty Username</font>"
        # We convert the a list to JSON data
        # https://flask.palletsprojects.com/en/1.1.x/quickstart/
        return jsonify(result)
    if username:
        if len(username) < 3:
            result["exists"] = True
            result["display"] = "<font color='red'> ❌ Too short username</font>"
            return jsonify(result)
        else:
            sql = "select * from user where username = (%s)"
            cur.execute(sql, (username,))
            user = cur.fetchone()
            if user:
                result["exists"] = True
                result["display"] = "<font color='red'> ❌ username \"" + username + "\" has been taken</font>"
            else:
                result["exists"] = False
                result["display"] = "<font color='green'> ✔ You can use this username. </font>"
            return jsonify(result)


@app.route('/game')
@app.route('/game.html')
def gaming2():
    if 'user' in session:
        game_users_before = []
        for user in game_users:
            game_users_before.append(user)
        game_users.append(session['user'])
        return render_template("game.html", sender=session['user'], players=game_users_before)
    else:
        redirecting = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="/login.html";}, 3000);</script>'
        return "<h1>Please login first.</h1>" + redirecting + rd_fail


@socketio.on('invite')
def invite(players):
    if 'user' in session:
        sender = players.get('sender')
        for user in online_users:
            if user not in game_users:
                emit('notice', {'sender': sender}, room=user)


@socketio.on('draw1')
def handleDraw(data):
    initX = data.get('initX')
    initY = data.get('initY')
    lastX = data.get('lastX')
    lastY = data.get('lastY')
    color = data.get('color')
    receiver = data.get('receiver')
    # print("x: " + str(data.get('axis_X')))
    # print("y: " + str(data.get('axis_Y')))
    for user in game_users:
        emit('draw2', {'initX': initX, 'initY': initY, 'lastX': lastX, 'lastY': lastY, 'color': color}, room=user)


@socketio.on('clear1')
def handleClear(data):
    height = data.get('height')
    for user in game_users:
        emit('clear2', {'height': height}, room=user)


@socketio.on('gameChat')
def gameChat(msg):
    if 'user' in session:
        sender = msg.get('sender')
        message = msg.get('message')
        for user in game_users:
            emit('gameChat2', {'sender': sender, 'message': escape(message)}, room=user)


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=8000)
    socketio.run(app, host='0.0.0.0', port=8000)
