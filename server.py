#/usr/bin/python3

"""The main HTTP server."""
from flask import Flask, render_template, jsonify, session, escape, redirect, url_for, request
from motor_util import MotorUtil
import scheduling
from auth import try_login, init_auth

app = Flask(__name__, static_url_path='/static')

@app.before_request
def intercept_login():
    if 'username' not in session and request.endpoint is not None and request.endpoint != 'login' and request.endpoint != 'static':
        return redirect(url_for('login'))
    return

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/')
def home():
    return render_template('index.j2', show_menu=True, show_refresh=True)

@app.route('/add_occurrence', methods=['POST'])
def add_occurrence():
    content = request.get_json(silent=True)
    day_id = content['day_id']
    hour = content['hour']
    minute = content['minute']

    if not scheduling.add_occurrence(day_id, hour, minute):
        response = {'status': 'error', error: 'Cannot add a duplicate occurrence.'}
        return jsonify(**response)    

    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/schedule')
def schedule():
    date = scheduling.get_next_occurrence()
    nextOccurrence = -1
    if date is not None:
        nextOccurrence = int(date.timestamp() * 1000)

    schedule = scheduling.get_recurrence_schedule()
    recurrences = []
    for recur in schedule:
        recurrences.append({'day_id': recur[0], 'hour': recur[1], 'minute': recur[2]})
    response = {'status': 'success', 'next_occurrence': nextOccurrence, 'schedule': recurrences}
    return jsonify(**response)

@app.route('/activate', methods=['POST'])
def activate():
    MotorUtil().turn_motor()
    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/login', methods=['GET', 'POST'])   
@app.route('/login/<error>', methods=['GET', 'POST'])   
def login(error=None):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if try_login(username, password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login', error='Wrong username or password.'))
    else:
        if 'username' in session:
            return redirect(url_for('home'))
        return render_template('login.j2', error_message=error, show_menu=False, show_refresh=False)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    scheduling.init_scheduler()
    init_auth()
    app.secret_key = 'a3ddad8e-2288-414e-9d7d-c5dd9018fef0'
    app.run(debug=True, host='0.0.0.0')
    