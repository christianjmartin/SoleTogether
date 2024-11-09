from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g
import logic
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'QEWOJFE3FIOENVWIOVCEI'

# Path to the database and SQL file
db_path = os.path.join(os.path.dirname(__file__), 'database.db')
sql_file_path = os.path.join(os.path.dirname(__file__), 'database.sql')

def init_db():
    with sqlite3.connect(db_path, check_same_thread=False) as conn:
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
        conn.executescript(sql_script)

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(db_path, check_same_thread=False)
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()








@app.route('/')
def index():
    session.clear()
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db()
        dbCursor = conn.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        session['username'] = username
        if logic.login(dbCursor, username, password):
            return render_template('menu.html')
        else:
            return jsonify(message='This client doesnt exist')
    else:
        return render_template('login.html')
    

@app.route ('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = get_db()
        dbCursor = conn.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        if logic.signup(conn, dbCursor, username, password):
            return render_template('menu.html')
        else:
            return jsonify(message='You already have an account, or an internal error occured')
    else:
        return render_template('signup.html')
    

with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)