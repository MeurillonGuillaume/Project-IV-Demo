import json
import logging
from os import urandom
from flask import Flask, session, request, render_template, redirect
from passlib.hash import bcrypt
from libs.spark import Spark
from libs.elastic import Elastic

# Load application secrets
secrets = json.load(open('./static/secrets.json'))

# Setup logging
logging.basicConfig(level=logging.INFO)

# Setup Flask
app = Flask(__name__)
app.secret_key = urandom(75)


# Setup Spark
# spark = Spark(secrets['spark']['server'], 'Project-IV-Demo-app', secrets['spark']['port'])

# Setup Elasticsearch
# elastic = Elastic(secrets['elastic']['server'], secrets['elastic']['port'])


def is_user_loggedin():
    """
    Check if a user is logged in
    :return: True or False
    """
    logging.info('Checking if user is logged in')
    if 'loggedin' in session:
        if session['loggedin']:
            logging.info('User is logged in')
            return True
    logging.warning('User is not logged in')
    return False


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Go to the homepage
    """
    if is_user_loggedin():
        return render_template('home.html', Loggedin=True)
    return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log a user in if possible or redirect home
    """
    logging.info('Attempting to login user')
    if not is_user_loggedin():
        if 'password' in request.form:
            if bcrypt.verify(request.form['password'], secrets['admin_password']):
                session['loggedin'] = True
                logging.info('User login successfull')
            else:
                logging.warning('User submitted a wrong password')
    return redirect('/')


@app.route('/logout')
def logout():
    """
    Log a user out if possible or redirect home
    """
    if is_user_loggedin():
        logging.info('Logging out')
        session['loggedin'] = False
    return redirect('/')


if __name__ == '__main__':
    app.run()
