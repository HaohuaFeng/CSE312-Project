from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')


@app.route('/')
@app.route('/default.html')
def home():
    return render_template('default.html')


@app.route('/new_login.html')
def login():
    return render_template('new_login.html')


@app.route('/new_register.html')
def register():
    return render_template('new_register.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
