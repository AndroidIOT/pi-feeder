import sqlite3
import bcrypt

def get_connection():
    """Gets a connection to the SQLite database."""
    return sqlite3.connect('pifeeder.db')

def get_hashed_password(plain_text_password):
    """Hashes a new password."""
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    """Compares a plain-text password to a hashed password."""
    return bcrypt.checkpw(plain_text_password, hashed_password)

def init_auth():
    """Creates database tables if they don't already exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS auth (_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, user TEXT NOT NULL, password TEXT NOT NULL)')
    hashed_pswd = get_hashed_password('feeder')

    cursor.execute('SELECT _id FROM auth')
    if cursor.fetchone() is None:
        cursor.execute('INSERT INTO auth (user, password) VALUES (?, ?);', ('admin', hashed_pswd))
        print("Added admin user.")

    conn.commit()
    conn.close()
    return

def try_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM auth WHERE user = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return check_password(password, result[0])

def try_change_password(username, current, new_password, confirm):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM auth WHERE user = ?', (username,))
    result = cursor.fetchone()
    
    if not check_password(current, result[0]):
        conn.close()
        return "Current password didn't match!"
    
    if new_password != confirm:
        conn.close()
        return "New password and confirmation didn't match!"

    hashed_pswd = get_hashed_password(new_password)
    cursor.execute('UPDATE auth SET password = ? WHERE user = ?', (hashed_pswd, username))

    conn.commit()
    conn.close()
    return None
