from flask import Flask, render_template, request, session, url_for, escape, send_file
from werkzeug.utils import redirect, escape
import pymysql
import os
import hashlib

# 在本地可以连接到MySQL server,放到docker上就不行了，查下怎么设置，参数，环境等等 db = pymysql.connect(host='db',user='root',password=os.getenv(
# 'MYSQL_PASSWORD'),db='zhong',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)
db = pymysql.connect(db="userdb", host='localhost',user='root', password="",charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)


cur = db.cursor()
cur.execute("create database IF NOT EXISTS zhong")
cur.execute("use zhong")
cur.execute("create table IF NOT EXISTS user(username varchar(50), password varchar(300));")
cur.execute("create table IF NOT EXISTS images(nm varchar(20), img LONGBLOB);")
# cur.execute("insert into user values(\"zhongai\",\"abc\")")
db.commit()

print("database and table created: success")

app = Flask(__name__)
app.secret_key = b'fjasldf;jlasfj#jfadlDJL23@ljfasljAi'


@app.route('/')
def hello_world():
    return render_template('default.html')
    # test image


#     fp = open("images/1.jpg",'rb')
#     img = fp.read()
#     print(img)
#     fp.close()
#     sql = "insert into images values (%s,%s);"
#     args = ("1.jpg",img)
#     cur.execute(sql,args)
#     db.commit()
#
#     if 'username' in session:
#         return "logged in as %s " % escape(session['username'])
#     return "please logged in!"


# @app.route('/images/<names>')
# def index(names=None):
#     sql = "select * from images where nm = %s"

#     cur.execute(sql,names)

#     name = cur.fetchone()
#     print("AAAAAAAAAAAAAAAAAAaa")
#     print(name['img'])
#     print(name['nm'])

#     return send_file("images/"+name['nm'])

# https://dormousehole.readthedocs.io/en/latest/quickstart.html#quickstart
@app.route('/new_login.html', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        print("username: " + username)
        print("password: " + password)
        print("session username: " + session['username'])
        # 一些判断语句验证，1：用户名是否存在 2：密码是否正确
        sql = "select * from user where username = (%s)"
        cur.execute(sql, (username))
        name = cur.fetchone()
        if name is None:
            return "no exist this username!"
        print("login name:" + name['username'])

        print(name)
        h = hashlib.sha256(password.encode())
        print("hashed password: " + h.hexdigest())
        if name['password'] == h.hexdigest():
            return "成功登入，欢迎回来： " + username +'<br>' + "<b><a href = '/reset'>Reset the password</a></b>"
        else:
            return "登入失败, 用户：" + username + " 密码错误"

    return render_template('new_login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('hello_world'))


@app.route('/new_register.html', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_check = request.form['pcheck']
        print("username: " + username)
        print("password: " + password)
        print("password_check: " + password_check)
        h = hashlib.sha256(password.encode())
        print("hashed hex  password: " + h.hexdigest())

        # 一些判断语句，比如输入空白提示，2次密码不同提示，用户名重复提示等等
        sql = "select * from user where username = (%s)"
        cur.execute(sql, (username))
        name = cur.fetchone()
        ex = 0
        if name is None:
            ex = 1
        if password != password_check:
            return "注册失败，two passwords don't match."
        elif ex == 0:
            return "注册失败，username \"" + username + "\" existed."

        # 新用户添加到database
        sql = "insert into user values (%s,%s)"
        cur.execute(sql, (username, h.hexdigest()))
        db.commit()
        return "注册成功，欢迎新用户: " + username
        # return render_template('register.html', rep=username,title="欢迎登入")
        # rep和title是html里面{{}}里的变量
    return render_template('new_register.html')


@app.route('/a')
def index2():
    if 'username' in session:
        username = session['username']
        return 'Logged in as ' + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
    return "You are not logged in <br><a href = '/new_login.html'>" + "click here to log in</a>"

@app.route('/reset',methods =['POST','GET'])
def resetpassword():

    if 'username' not in session:
        return redirect('/new_login.html')
    username = session['username']
    if request.method == "POST":
        old_password = request.form['oldpassword']   
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password !=confirm_password:
            return "Two new passwords does not match <br><a href = '/reset'>" + "click here to reset again</a>"
        print(username)
        print(password)
        password = hashlib.sha256(password.encode())
        old_password = hashlib.sha256(old_password.encode())
        print(password)
        print("hashed hex  password: " + password.hexdigest())
        #cur=db.cursor()
        result= cur.execute("SELECT * FROM user Where username=%s", [username])

        if result >0:
            user=cur.fetchone()
            print(result)
            print(old_password)
            originpassword=user['password']
            print(originpassword)
            newpassword=password.hexdigest()
            if old_password.hexdigest() != originpassword:
                return "Old password is incorrect <br><a href = '/reset'>" + "click here to to reset again</a>"

            if newpassword==originpassword:
                return "Old password can not be used as new password in order to improve your account security<br><a href = '/reset'>" + "click here to reset again</a>"

            cur.execute("UPDATE user SET password=%s WHERE username=%s",(newpassword,username))
            db.commit()
            return "Updated successfully <br><a href = '/a'>" + "click here to the home page</a>"
            
    return render_template('reset.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
