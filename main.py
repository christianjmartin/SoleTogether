from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g
import logic
import sqlite3
import os
import requests

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
    

@app.route('/menu')
def menu():
    return render_template('menu.html')

def fetch_sneaker_brands():
    url = "https://v1-sneakers.p.rapidapi.com/v1/brands"
    headers = {
        "x-rapidapi-host": "v1-sneakers.p.rapidapi.com",
        "x-rapidapi-key": "8b1bac8483msh1e8e12c443cd7cbp1192cejsn4ab3a1e0147d"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        brands = response.json()
        print("Sneaker Brands:", brands)
        return brands
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")



@app.route('/search', methods=['POST'])
def search_sneakers():
    keyword = request.form.get('keyword')
    url = f"https://{API_HOST}/v1/sneakers"
    headers = {
        "x-rapidapi-host": API_HOST,
        "x-rapidapi-key": API_KEY
    }
    params = {"limit": 10, "name": keyword}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        sneakers = response.json().get('results', [])
        return jsonify(sneakers)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return jsonify({"error": "HTTP error occurred"}), 500
    except Exception as err:
        print(f"An error occurred: {err}")
        return jsonify({"error": "An error occurred"}), 500


@app.route('/discussion', methods=['GET'])
def view_discussion():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    dbCursor = conn.cursor()
    entries = logic.get_discussion_entries(dbCursor)
    user_stats = logic.get_user_stats(dbCursor, session['username'])
    
    return render_template(
        'discussion.html',
        entries=entries,
        current_user=session['username'],
        user_stats=user_stats
    )

@app.route('/discussion/create', methods=['POST'])
def create_entry():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    body = request.form.get('body')
    if not body:
        return jsonify({'error': 'Empty post'}), 400
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    if logic.create_discussion_entry(conn, dbCursor, session['username'], body):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to create entry'}), 500

@app.route('/discussion/like/<int:entry_id>', methods=['POST'])
def like_entry(entry_id):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    # Get client ID for the current user
    dbCursor.execute("SELECT ClientID FROM Client WHERE Username = ?", 
                    (session['username'],))
    result = dbCursor.fetchone()
    if not result:
        return jsonify({'error': 'User not found'}), 404
    
    client_id = result[0]
    if logic.toggle_like(conn, dbCursor, client_id, entry_id):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to toggle like'}), 500

@app.route('/user/follow/<username>', methods=['POST'])
def follow_user(username):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    if username == session['username']:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    if logic.toggle_follow(conn, dbCursor, session['username'], username):
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Failed to toggle follow'}), 500


with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)