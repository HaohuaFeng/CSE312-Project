from flask import Flask, render_template, request, session, url_for
from werkzeug.utils import redirect, escape
import pymysql
import os
import hashlib
# 导入时间lib
from datetime import datetime
from flask_socketio import SocketIO, emit, send, join_room,leave_room
import json
import base64
# 在本地可以连接到MySQL server,放到docker上就不行了，查下怎么设置，参数，环境等等
# db = pymysql.connect(host='db', user='root', password=os.getenv(
#     'MYSQL_PASSWORD'), db='zhong', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
db = pymysql.connect(host='localhost', user='root', charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

cur = db.cursor()
cur.execute("create database IF NOT EXISTS zhong")
cur.execute("use zhong")
cur.execute(
    "create table IF NOT EXISTS user(username varchar(200), email varchar(50), password varchar(300),icon varchar("
    "200) default 'fakeuser.png', gender varchar(10), birth varchar(20), personal_page varchar(100), introduction "
    "varchar(500));")
cur.execute(
    "create table IF NOT EXISTS blog(image varchar(200), comment varchar(500), "
    "username varchar(200), date varchar(20));")
cur.execute("create table IF not EXISTS online_status(username varchar(200), online boolean default False);")
cur.execute("alter table user convert to character set utf8mb4 collate utf8mb4_bin;")
cur.execute("alter table blog convert to character set utf8mb4 collate utf8mb4_bin;")
db.commit()

app = Flask(__name__)
app.secret_key = b'fjasldf;jlasfj#jfadlDJL23@ljfasljAi'
app.config['SECRET_KEY'] = 'mysecret'
socketio = SocketIO(app)


@app.route('/', methods=['POST', 'GET'])
@app.route('/index', methods=['POST', 'GET'])
@app.route('/index.html', methods=['POST', 'GET'])
def hello_world():
    if 'user' in session:
        username = session['user']
    else:
        username = None

    sql2 = "select * from blog"
    cur.execute(sql2)
    blogs = cur.fetchall()

    # show online user
    if 'user' in session:
        online = "SELECT * FROM user INNER JOIN online_status ON user.username=online_status.username " \
                 "WHERE online=%s AND online_status.username<>%s"
        cur.execute(online, (True, session['user']))
    else:
        online = "SELECT * FROM user INNER JOIN online_status ON user.username=online_status.username " \
                 "WHERE online=%s"
        cur.execute(online, True)
    users = cur.fetchall()
    return render_template('index.html', user=username, blogs=blogs, users=users)


@socketio.on('send-message', namespace='/test')
def display(message):
    if 'user' in session:
        username = session['user']
    else:
        username = None
    comment = message['comment']
    image_filename = ""
    if 'image' in message.keys():
        image = message['image']
        image_index = image.find('base64,')
        image_byte = base64.b64decode(image[image_index + len('base64,'):])

        cur.execute("select * from blog")
        num = len(cur.fetchall())

        image_filename = "image" + str(num) + ".jpg"
        with open("static/images/" + image_filename, "wb") as file:
            file.write(image_byte)
            file.close()

    now = datetime.now()
    date = now.strftime("%d/%m/%Y %H:%M:%S")

    sql = "insert into blog values (%s,%s,%s,%s)"
    cur.execute(sql, (image_filename, comment, username, date))
    db.commit()


    if 'user' in session:
        online = "SELECT * FROM user INNER JOIN online_status ON user.username=online_status.username " \
                 "WHERE online=%s AND online_status.username<>%s"
        cur.execute(online, (True, session['user']))
    else:
        online = "SELECT * FROM user INNER JOIN online_status ON user.username=online_status.username " \
                 "WHERE online=%s"
        cur.execute(online, True)
    #online users no complete yet.
    emit('blog_done', {'user': username, 'date': date, 'comment': comment, 'image': image_filename}, broadcast=True)


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
        cur.execute(sql, username)
        name = cur.fetchone()
        redirect = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="login.html";}, 3000);</script>'
        rd_suc = '<script>setTimeout(function(){window.location.href="index.html";}, 3000);</script>'
        if name is None:
            return "<h1>This username does not exist!</h1>" + redirect + rd_fail
        cur.execute("SELECT online FROM online_status WHERE username=%s", username)
        online = cur.fetchall()
        if online == 1:
            rd_online = '<script>setTimeout(function(){window.location.href="login.html";}, 3000);</script>'
            return "<h1>User " + username + " is online<br>If you believe your password has been compromised, please " \
                                            "change your password</h1>" + redirect + rd_online
        h = hashlib.sha256(password.encode())
        if name['password'] == h.hexdigest():
            session['user'] = username
            cur.execute("UPDATE online_status SET online=%s WHERE username=%s", (True, username))
            db.commit()
            return "<h1>成功登入，欢迎回来： " + username + "</h1>" + redirect + rd_suc
        else:
            return "<h1>登入失败, 用户：" + username + " 密码错误</h1>" + redirect + rd_fail
    if 'user' in session:
        return render_template('login.html', user=session['user'])
    return render_template('login.html')


@app.route('/forgot.html', methods=['POST', 'GET'])
def forgot():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']

        # 一些判断语句验证，1：用户名是否存在 2：密码是否正确
        sql = "select * from user where username = (%s)"
        cur.execute(sql, username)
        name = cur.fetchone()
        redirect = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="forgot.html";}, 3000);</script>'
        rd_suc = '<script>setTimeout(function(){window.location.href="login.html";}, 5000);</script>'
        if name is None:
            return "<h1>This username does not exist!</h1>" + redirect + rd_fail

        if name['email'] == email:
            newpassword = 'abcd1234'
            newpassword_hash = hashlib.sha256(newpassword.encode())
            cur.execute("UPDATE user SET password=%s WHERE username=%s", (newpassword_hash.hexdigest(), username))
            db.commit()
            return "<h1>Hello, " + username + ", your new password is <span style='color:blue'>" + newpassword + \
                   "</span>. This password is not secure, please change it immediately.</h1>" + redirect + rd_suc
        else:
            return "<h1>Either username or email is incorrect.</h1>" + redirect + rd_fail

    return render_template('forgot.html')


@app.route('/logout')
def logout():
    cur.execute("UPDATE online_status SET online=%s WHERE username=%s", (False, session['user']))
    db.commit()
    session.pop('user', None)
    redirect = '<h3>Redirecting ... </h3>'
    rd_suc = '<script>setTimeout(function(){window.location.href="login.html";}, 3000);</script>'
    return "<h1>You have logout successfully.</h1>" + redirect + rd_suc


@app.route('/register.html', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_check = request.form['pcheck']
        h = hashlib.sha256(password.encode())
        # 一些判断语句，比如输入空白提示，2次密码不同提示，用户名重复提示等等
        sql = "select * from user where username = (%s)"
        cur.execute(sql, username)
        name = cur.fetchone()
        ex = 0
        redirect = '<h3>Redirecting ... </h3>'
        rd_fail = '<script>setTimeout(function(){window.location.href="register.html";}, 3000);</script>'
        rd_suc = '<script>setTimeout(function(){window.location.href="login.html";}, 3000);</script>'
        rd_suc2 = '<script>setTimeout(function(){window.location.href="index.html";}, 3000);</script>'
        if name is None:
            ex = 1
        if password != password_check:
            return "<h1>注册失败，two passwords don't match.</h1>" + redirect + rd_fail
        elif ex == 0:
            return "<h1>注册失败，username \"" + username + "\" existed.</h1>" + redirect + rd_fail

        # 新用户添加到database
        sql = "insert into user(username,email,password) values (%s,%s,%s)"
        cur.execute(sql, (username, email, h.hexdigest()))

        # insert online status
        online = "insert into online_status(username) value(%s)"
        cur.execute(online, username)
        db.commit()
        if 'user' in session:
            return "<h1>注册成功，欢迎新用户: " + username + ".</h1>" + redirect + rd_suc2
        else:
            return "<h1>注册成功，欢迎新用户: " + username + ".</h1>" + redirect + rd_suc
        # return render_template('register.html', rep=username,title="欢迎登入")
        # rep和title是html里面{{}}里的变量
    if 'user' in session:
        return render_template('register.html', user=session['user'])
    return render_template('register.html')


@app.route('/a')
def index2():
    if 'user' in session:
        username = session['user']
        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
    return "You are not logged in <br><a href = '/login.html'>" + "click here to log in</a>"


@app.route('/reset', methods=['POST', 'GET'])
def resetpassword():
    if 'username' not in session:
        return redirect('/login.html')
    username = session['user']
    if request.method == "POST":
        old_password = request.form['oldpassword']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            return "Two new passwords does not match <br><a href = '/reset'>" + "click here to reset again</a>"
        print(username)
        print(password)
        password = hashlib.sha256(password.encode())
        old_password = hashlib.sha256(old_password.encode())
        print(password)
        print("hashed hex  password: " + password.hexdigest())
        # cur=db.cursor()
        result = cur.execute("SELECT * FROM user Where username=%s", [username])

        if result > 0:
            user = cur.fetchone()
            print(result)
            print(old_password)
            originpassword = user['password']
            print(originpassword)
            newpassword = password.hexdigest()
            if old_password.hexdigest() != originpassword:
                return "Old password is incorrect <br><a href = '/reset'>" + "click here to to reset again</a>"

            if newpassword == originpassword:
                return "Old password can not be used as new password in order to improve your account security<br><a href = '/reset'>" + "click here to reset again</a>"

            cur.execute("UPDATE user SET password=%s WHERE username=%s", (newpassword, username))
            db.commit()
            return "Updated successfully <br><a href = '/a'>" + "click here to the home page</a>"

    return render_template('profile.html')


@app.route('/profile', methods=['POST', 'GET'])
@app.route('/profile.html', methods=['POST', 'GET'])
def profile():
    if request.method == "POST":
        email = request.form['email']
        gender = request.form['gender']
        birth = request.form['birth']
        pp = request.form['personal_page']
        introduction = request.form['introduction']
        icon = request.files['icon']
        ic = icon.read()
        path = "static/images/" + icon.filename
        fout = open(path, 'wb')
        fout.write(ic)
        fout.close()
        print(email + " " + gender + " " + birth + " " + pp + " " + introduction + " " + icon.filename)
        sql = "update user set email=%s,icon=%s,gender=%s,birth=%s,personal_page=%s,introduction=%s where username=%s"
        cur.execute(sql, (email, icon.filename, gender, birth, pp, introduction, session['user']))
        db.commit()

    if 'user' in session:
        username = session['user']
        sql = "select * from user where username = (%s)"
        cur.execute(sql, username)
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

    return "Please login first."

@app.route('/direct_chat/<send_to_user>')
def directChat(send_to_user):
    if 'user' in session:
        sender = session['user']
        return render_template("direct_chat.html",sender=sender,send_to=send_to_user)
    else:
        return "Please log in"

@socketio.on('message',namespace='/direct_chat')
def handleMessage(msg):
    print("message: " + msg)
    send(msg,broadcast=True)

@app.route('/user_profile/<look_user>')
def userProfile(look_user):
    sql = "select * from user where username = (%s)"
    cur.execute(sql, look_user)
    look_user = cur.fetchone()
    if 'user' in session:
        user = session['user']
        return render_template("user_profile.html",user=user,look_user=look_user)
    else:
        return render_template("user_profile.html",look_user=look_user)


if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=8000)
    socketio.run(app, host='0.0.0.0', port=8000)