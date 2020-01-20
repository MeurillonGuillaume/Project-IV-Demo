from flask import Flask, session, request, render_template
from os import urandom
from passlib.hash import bcrypt

app = Flask(__name__)
app.secret_key = urandom(75)


@app.route('/')
def home():
    """
    Go to the homepage
    """
    if 'loggedin' in session:
        return render_template('index.html')
    else:
        return render_template('login.html')


if __name__ == '__main__':
    app.run()
