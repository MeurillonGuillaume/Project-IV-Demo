import json
import logging
from os import urandom
from flask import Flask, session, request, render_template, redirect
from passlib.hash import bcrypt
from libs.spark import Spark
from libs.elastic import Elastic
from libs.timer import Timer
from libs.threader import Threader

ACTIVE_INDICES = set()
LOADED_INDICES = set()
PREV_RESPONSE = ''
PREV_RESPONSETIME = 0
PREV_QUERY = ''
# Load application secrets
secrets = json.load(open('./static/secrets.json'))

# Setup logging
logging.basicConfig(level=logging.INFO)

# Setup Flask
app = Flask(__name__)
app.secret_key = urandom(75)

# Setup Spark
spark = Spark(secrets['spark']['server'], 'Project-IV-Demo-app', secrets['elastic']['version'],
              secrets['elastic']['internal'], secrets['spark']['port'])

# Setup Elasticsearch
elastic = Elastic(secrets['elastic']['server'], secrets['elastic']['port'])

# Create timer
timer = Timer()

# Create threader
threader = Threader()


def load_dataset(idx):
    global LOADED_INDICES, ACTIVE_INDICES
    if idx not in LOADED_INDICES:
        logging.info(f'Loading index {idx} into Spark')
        spark.load_index(idx)
        LOADED_INDICES.add(idx)
        ACTIVE_INDICES.add(idx)


def reload_datasets_into_memory():
    global ACTIVE_INDICES, LOADED_INDICES
    for idx in elastic.get_user_indices():
        if idx in LOADED_INDICES:
            logging.info(f'Loading index {idx} into Spark')
            spark.load_index(idx)


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


@app.route('/reload')
def reload():
    """
    Reload datasets
    """
    reload_datasets_into_memory()
    return redirect('/')


@app.route('/fullresult')
def fullresult():
    """
    Return the full query result
    """
    if is_user_loggedin():
        return json.dumps(PREV_RESPONSE, indent=4)
    return redirect('/')


@app.route('/load')
def load():
    if is_user_loggedin():
        load_dataset(request.args.get('index'))
    return redirect('/')


@app.route('/unload')
def unload():
    global LOADED_INDICES, ACTIVE_INDICES
    if is_user_loggedin():
        idx = request.args.get('index')
        spark.drop_index(idx)
        LOADED_INDICES.remove(idx)
        ACTIVE_INDICES.remove(idx)
    return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Go to the homepage
    """
    if is_user_loggedin():
        if len(PREV_RESPONSE) > 10000:
            return render_template('home.html', Loggedin=True, Indices=elastic.get_user_indices(),
                                   Elastichost=secrets['elastic']['server_exteral'],
                                   Elasticport=secrets['elastic']['port'], Grafanaserver=secrets['grafana']['server'],
                                   Grafanaport=secrets['grafana']['port'],
                                   Response=f'{str(PREV_RESPONSE)[0:10000]} ...',
                                   ResponseTooLong=True,
                                   Responsetime=PREV_RESPONSETIME, Prevquery=PREV_QUERY, Activeindices=ACTIVE_INDICES)
        elif 1 < len(PREV_RESPONSE) < 10000:
            return render_template('home.html', Loggedin=True, Indices=elastic.get_user_indices(),
                                   Elastichost=secrets['elastic']['server_exteral'],
                                   Elasticport=secrets['elastic']['port'], Grafanaserver=secrets['grafana']['server'],
                                   Grafanaport=secrets['grafana']['port'],
                                   Response=PREV_RESPONSE,
                                   Responsetime=PREV_RESPONSETIME, Prevquery=PREV_QUERY, Activeindices=ACTIVE_INDICES)
        else:
            return render_template('home.html', Loggedin=True, Indices=elastic.get_user_indices(),
                                   Elastichost=secrets['elastic']['server_exteral'],
                                   Elasticport=secrets['elastic']['port'], Grafanaserver=secrets['grafana']['server'],
                                   Grafanaport=secrets['grafana']['port'], Activeindices=ACTIVE_INDICES)
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


@app.route('/query', methods=['GET', 'POST'])
def query():
    global PREV_RESPONSE, PREV_RESPONSETIME, PREV_QUERY
    if is_user_loggedin():
        if 'query' in request.form and 'querytype' in request.form and 'querysource' in request.form and 'threads' in request.form:
            threads = int(request.form['threads'])
            running_threads = len(threader.check_threads()) + 1
            PREV_QUERY = request.form['query']
            try:
                timer.start()
                if request.form['querytype'] == 'sql':
                    if request.form['querysource'] == 'elastic':
                        if threads == 1:
                            PREV_RESPONSE = elastic.query_sql(request.form['query'])
                        elif threads > 1:
                            threader.launch_threads(elastic.query_sql, threads, (request.form['query'],))
                            while len(threader.check_threads()) > running_threads:
                                # waste cycles
                                ...
                            PREV_RESPONSE = json.dumps({"status": "All threads have finished successfully"}, indent=4)
                    elif request.form['querysource'] == 'spark':
                        if threads == 1:
                            PREV_RESPONSE = spark.query_spark_sql(request.form['query'])
                        elif threads > 1:
                            threader.launch_threads(spark.query_spark_sql_fast, threads, (request.form['query'],))
                            while len(threader.check_threads()) > running_threads:
                                # waste cycles
                                ...
                            PREV_RESPONSE = json.dumps({"status": "All threads have finished successfully"}, indent=4)
                elif request.form['querytype'] == 'dsl' and request.form['querysource'] == 'elastic':
                    if threads == 1:
                        PREV_RESPONSE = elastic.query_dsl(request.form['query'], request.form['index'])
                    elif threads > 1:
                        threader.launch_threads(elastic.query_dsl, threads,
                                                (request.form['query'], request.form['index']))
                        while len(threader.check_threads()) > running_threads:
                            # waste cycles
                            ...
                        PREV_RESPONSE = json.dumps({"status": "All threads have finished successfully"}, indent=4)
                PREV_RESPONSETIME = timer.stop()
            except Exception as e:
                logging.error(f'Error querying: {e}')
                PREV_RESPONSE = f'Something went wrong: {e}'
            logging.info(
                f'Requesting query of type {request.form["querytype"]} on {request.form["querysource"]}: "{request.form["query"]}"')
        return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False, port=5000)
