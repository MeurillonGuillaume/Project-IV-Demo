from flask import Flask, session, request, render_template, redirect
from os import urandom
import json
from passlib.hash import bcrypt

secrets = json.load(open('./static/secrets.json'))

app = Flask(__name__)
app.secret_key = urandom(75)


def is_user_loggedin():
    if 'loggedin' in session:
        if session['loggedin']:
            return True
    return False


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Go to the homepage
    """
    if is_user_loggedin():
        return render_template('index.html', Loggedin=True)
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if not is_user_loggedin():
        if 'password' in request.form:
            if bcrypt.verify(request.form['password'], secrets['admin_password']):
                session['loggedin'] = True
    return redirect('/')


@app.route('/logout')
def logout():
    if is_user_loggedin():
        session['loggedin'] = False
    return redirect('/')


if __name__ == '__main__':
    app.run()
