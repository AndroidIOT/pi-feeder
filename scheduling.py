#/usr/bin/python3

"""Scheduling read/write utils."""
import sqlite3
import threading
from time import sleep
from string import Formatter as sform
from datetime import datetime as dt
from date_utils import *
from motor_util import MotorUtil

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6

IS_INIT = False

def day_diff(src, dst, next_week=False):
    if src == dst and next_week:
        return 7
    elif dst > src:
        return dst - src
    count = 0
    index = 0
    while index != dst:
        count = count + 1
        index = index + 1
        if index > 6: 
            index = 0
    return count

def check_should_activate(recurrence):
    """Checks if the feeder should be activated right now."""
    now = right_now()
    return int(recurrence.weekday()) == int(now.weekday()) and int(recurrence.hour) == int(now.hour) and int(recurrence.minute) == int(now.minute)

def ticker():
    """The ticker which checks if a schedule moment has been reached."""
    print("Started!")
    while True:
        next_occurrence = get_next_occurrence()
        if next_occurrence is not None:
            if check_should_activate(next_occurrence):
                print("Schedule has triggered!")
                MotorUtil().turn_motor()
        else:
            sleep(25)
        sleep(20)
    print("Ticker has quit!")
    return

THREAD = threading.Thread(target=ticker)

def get_connection():
    """Gets a connection to the SQLite database."""
    return sqlite3.connect('pifeeder.db')

def init_scheduler():
    """Creates database tables if they don't already exist."""

    global IS_INIT
    if IS_INIT:
        print("Scheduler was already initialized!")
        return
    IS_INIT = True

    print("Setting up databases...")
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS recurrence (day_id INTEGER NOT NULL, hour INTEGER NOT NULL, minute INTEGER NOT NULL)')
    conn.commit()
    conn.close()

    print("Starting ticker...")
    THREAD.start()
    return

def get_recurrence_schedule():
    """Gets the ongoing daily recurrence schedule."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM recurrence ORDER BY day_id, hour, minute')
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_occurrence(day_id, hour, minute):
    """Adds a recurrence to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM recurrence WHERE day_id = ? AND hour = ? AND minute = ?', (day_id, hour, minute))
    if cursor.fetchone() is not None:
        return False

    cursor.execute('INSERT INTO recurrence (day_id, hour, minute) VALUES (?, ?, ?);', (day_id, hour, minute))
    conn.commit()
    conn.close()
    return True

def get_next_occurrence():
    """Gets the next today/time for which the feeder will activate."""
    today = right_now()
    conn = get_connection()
    cursor = conn.cursor()

    # Try to find a next occurrence in the current week (before an ending Sunday).
    # Will be today within the remaining hours/minutes, or another day in the current week.
    cmd = sform().format('SELECT * FROM recurrence WHERE (day_id = {0} AND hour > {1} AND minute > {2}) OR (day_id = {0} AND hour = {1} AND minute > {2}) OR (day_id > {0}) ORDER BY day_id, hour, minute', 
        today.weekday(), today.hour - 1, today.minute - 1)
    cursor.execute(cmd)
    result = cursor.fetchone()

    if result is not None:
        # Found a next recurrence today, or within this week
        if result[0] == today.weekday():
            # today
            conn.close()
            return dt(today.year, today.month, today.day, result[1], result[2])
        else:
            # after today
            days_diff = day_diff(today.weekday(), result[0])
            target = add_days(today, days=days_diff)
            conn.close()
            return dt(target.year, target.month, target.day, result[1], result[2])

    if result is None:
        # Didn't find recurrence today or within the remaining week, check next week
        cmd = sform().format('SELECT * FROM recurrence WHERE (day_id < {0}) OR (day_id = {0} AND hour = {1} AND minute < {2}) OR (day_id = {0} AND hour < {1}) ORDER BY day_id, hour, minute',
            today.weekday(), today.hour, today.minute)
        cursor.execute(cmd)
        result = cursor.fetchone()

        if result is not None:
            # Found a recurrence for previous week days, for next week
            days_diff = day_diff(today.weekday(), result[0], True)
            target = add_days(today, days_diff)
            conn.close()
            return dt(target.year, target.month, target.day, result[1], result[2])

    conn.close()
    return None
    