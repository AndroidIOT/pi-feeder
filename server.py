#/usr/bin/python3

"""The main HTTP server."""
from flask import Flask, render_template, jsonify, session, escape, redirect, url_for, request
from motor_util import MotorUtil
from auth import try_login, init_auth, try_change_password
from datetime import timedelta
import scheduling
from discovery import init_visibility

app = Flask(__name__, static_url_path='/static')

@app.before_request
def intercept_login():
    """Intercepts every request and checks if the user is logged in."""
    if 'username' not in session and request.endpoint is not None and request.endpoint != 'login' and request.endpoint != 'static':
        return redirect(url_for('login'))
    
    # Sessions last for 30 minutes before having to login again
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)

    return

@app.after_request
def add_header(response):
    """Makes sure no requests are ever cached by browsers."""
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route('/')
def home():
    """The homepage, after logging in."""
    return render_template('index.j2', show_menu=True, show_refresh=True)

@app.route('/add_recurrence', methods=['POST'])
def add_recurrence():
    """API: adds an occurrence to the recurrence schedule."""
    content = request.get_json(silent=True)
    day_id = content['day_id']
    hour = content['hour']
    minute = content['minute']

    if not scheduling.add_occurrence(day_id, hour, minute):
        response = {'status': 'error', error: 'Cannot add a duplicate occurrence.'}
        return jsonify(**response)    

    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/remove_recurrence', methods=['POST'])
def remove_recurrence():
    """API: removes an occurrence from the recurrence schedule."""
    content = request.get_json(silent=True)
    day_id = content['day_id']
    hour = content['hour']
    minute = content['minute']
    scheduling.remove_recurrence(day_id, hour, minute)
    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/add_onetime_occurrence', methods=['GET', 'POST'])
@app.route('/add_onetime_occurrence/<error>', methods=['GET', 'POST'])
def add_onetime_occurrence(error=None):
    """API: the modal for adding a one-time occurrence to the schedule."""
    if request.method == 'POST':
        content = request.get_json(silent=True)
        year = content['year']
        month = content['month']
        day = content['day']
        hour = content['hour']
        minute = content['minute']
        
        if not scheduling.add_onetime_occurrence(year, month, day, hour, minute):
            response = {'status': 'error', error: 'Cannot add a duplicate occurrence.'}
            return jsonify(**response)    

        response = {'status': 'success'}
        return jsonify(**response)
    else:
        return render_template('onetimemodal.j2', error_message=error)

@app.route('/remove_onetime_occurrence', methods=['POST'])
def remove_onetime_occurrence():
    """API: removes an occurrence from the recurrence schedule."""
    content = request.get_json(silent=True)
    year = content['year']
    month = content['month']
    day = content['day']
    hour = content['hour']
    minute = content['minute']
    scheduling.remove_onetime_occurrence(year, month, day, hour, minute)
    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/schedule')
def schedule():
    """API: retrieves the full reoccurrence schedule."""
    date = scheduling.get_next_occurrence()
    nextOccurrence = -1
    if date is not None:
        nextOccurrence = int(date.timestamp() * 1000)

    schedule = scheduling.get_recurrence_schedule()
    recurrences = []
    for recur in schedule:
        recurrences.append({'day_id': recur[0], 'hour': recur[1], 'minute': recur[2]})

    onetimeschedule = scheduling.get_onetime_occurrence_schedule()
    occurrences = []
    for recur in onetimeschedule:
        occurrences.append({'year': recur[0], 'month': recur[1], 'day': recur[2], 'hour': recur[3], 'minute': recur[4]})

    response = {'status': 'success', 'next_occurrence': nextOccurrence, 'schedule': recurrences, 'onetimes': occurrences}
    return jsonify(**response)

@app.route('/activate', methods=['POST'])
def activate():
    """Triggers the feeder now."""
    MotorUtil().turn_motor()
    response = {'status': 'success'}
    return jsonify(**response)

@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/<error>', methods=['GET', 'POST'])
def login(error=None):
    """Loads the login page or performs login."""
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

@app.route('/settings', methods=['GET', 'POST'])
@app.route('/settings/<error>', methods=['GET', 'POST'])
def settings(error=None):
    """Loads the settings page or saves settings.."""
    if request.method == 'POST':
        username = session['username']
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        try_result = try_change_password(username, current_password, new_password, confirm_password)
        if try_result is not None:
            return render_template('settings.j2', error_message=try_result, show_menu=True, show_refresh=False)    
        return redirect(url_for('home'))
    else:
        return render_template('settings.j2', error_message=error, show_menu=True, show_refresh=False)

@app.route('/logout')
def logout():
    """Nullifies the session."""
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    scheduling.init_scheduler()
    init_auth()
    init_visibility()
    app.secret_key = 'a3ddad8e-2288-414e-9d7d-c5dd9018fef0'
    app.run(debug=True, host='0.0.0.0')
    