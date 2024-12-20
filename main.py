from flask import Flask, render_template, request, redirect, url_for, jsonify, session, g
import logic
import sqlite3
import os
import requests
import json
import time
from dataclasses import dataclass

app = Flask(__name__)
app.secret_key = 'QEWOJFE3FIOENVWIOVCEI'

NODE_API_URL = "http://localhost:5001"

@dataclass
class Sneaker:
    resell_price: int
    brand: str
    name: str
    price: float
    img_url: str
    sku: str
    release_date: str
    description: str
    stockx_link: str = None
    goat_link: str = None
    flightclub_link: str = None

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

def fetch_top_items(brand):
    api_url = f"http://localhost:5001/sneakers?query={brand}&limit=4"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json() 
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return []

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
            # conn = get_db()
            # dbCursor = conn.cursor()
            username = session['username']
            # user_brands = logic.get_user_brands(dbCursor, username)
            return redirect(url_for('menu'))
            # return render_template('menu.html')
        else:
            return jsonify(message='This client doesnt exist')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        conn = get_db()
        dbCursor = conn.cursor()
        username = request.form.get('username')
        password = request.form.get('password')
        session['username'] = username
        if logic.signup(conn, dbCursor, username, password):
            return redirect(url_for('tutorial1'))
        else:
            return jsonify(message='You already have an account, or an internal error occured')
    else:
        return render_template('signup.html')

@app.route('/menu')
def menu():
    conn = get_db()
    dbCursor = conn.cursor()
    username = session['username']
    user_brands = logic.get_user_brands(dbCursor, username)

    if user_brands:
        # THE NUMBER IS HOW OFTEN IT CHANGES, NOW ITS EVERY 5 SECONDS FOR TESTING PURPOSES
        index = int(time.time() // 5) % len(user_brands)  # Changes every 30 seconds
        brand_to_display = user_brands[index]
        with app.test_client() as client:
            response = client.get(f"/sneaker_search_results?keyword={brand_to_display}&limit=25")
            if response.status_code == 200:
                top_four = response.get_json()[:4]
                for i in top_four:
                    print(i)
                    print()
            else:
                print(f"Error: {response.get_json().get('error', 'Unknown error')}")
                top_four = []
    else:
        top_four = []

    processed_sneakers = []
    for sneaker in top_four:
        try:
            average_price = 0
            resell_prices = sneaker.get('lowestResellPrice')
            if resell_prices:
                price_values = resell_prices.values()
                if price_values:
                    average_price = round(sum(price_values) / len(price_values))
                else:
                    average_price = None
            else:
                average_price = sneaker.get('retailPrice')

            # resell_links = sneaker.get('resellLinks', {})
            # stockx_link = resell_links.get('stockX', None)
            # goat_link = resell_links.get('goat', None)
            # flightclub_link = resell_links.get('flightClub', None)

            # Create a Sneaker object for each sneaker
            sneaker_obj = Sneaker(
                resell_price=average_price,
                brand=sneaker.get('brand'),
                name=sneaker.get('shoeName'),
                price=None,
                img_url=sneaker.get('thumbnail'),
                sku=sneaker.get('styleID'),
                release_date=None,
                description=None,
                stockx_link=None,
                goat_link=None,
                flightclub_link=None
            )

            processed_sneakers.append(sneaker_obj)

        except Exception as e:
            print(f"Error processing sneaker: {e}")
            continue

    conn.close()
    
    return render_template(
        'menu.html',
        top_four=processed_sneakers
    )


@app.route('/tutorial1', methods=['GET', 'POST'])
def tutorial1():
    if request.method == 'POST':
        brands_json = request.form.get('selected_brands')
        brands = json.loads(brands_json)
        # for brand in brands:
        #     print(brand)
        conn = get_db()
        dbCursor = conn.cursor()
        username = session['username']
        insert_brands = logic.insert_brands(conn, dbCursor, username, brands)
        if insert_brands:
            return redirect(url_for('tutorial2'))
        else:
            return jsonify(message='Error in saving your brands')
    else:
        return render_template('tutorial1.html')

@app.route('/tutorial2', methods=['GET', 'POST'])
def tutorial2():
    if request.method == 'POST':
        return redirect(url_for('tutorial3'))
    else:
        return render_template('tutorial2.html')
    
@app.route('/tutorial3', methods=['GET', 'POST'])
def tutorial3():
    if request.method == 'POST':
        return redirect(url_for('tutorial4'))
    else:
        return render_template('tutorial3.html')
    
@app.route('/tutorial4', methods=['GET', 'POST'])
def tutorial4():
    if request.method == 'POST':
        # conn = get_db()
        # dbCursor = conn.cursor()
        # username = session['username']
        # user_brands = logic.get_user_brands(dbCursor, username)
        return redirect(url_for('menu'))
    else:
        return render_template('tutorial4.html')
    






@app.route('/sneakerSearch', methods=['POST'])
def search_page():
    return render_template('sneakerSearch.html')

@app.route('/sneaker_search_results', methods=['GET'])
def search_sneakers():
    keyword = request.args.get('keyword', '')
    limit = request.args.get('limit', 25) 
    try:
        response = requests.get(f"{NODE_API_URL}/sneakers", params={"keyword": keyword, "limit": limit})
        response.raise_for_status()
        sneakers = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Sneaks-API: {e}")
        return jsonify({"error": "Failed to fetch sneakers. Please try again later."}), 500

    return jsonify(sneakers)

@app.route('/sneakerpage', methods=['GET', 'POST'])
def sneaker_page():
    sku = request.args.get('sku') if request.method == 'GET' else request.form.get('sku')
    if not sku:
        return "Error: Missing shoe_id", 400

    conn = get_db()
    dbCursor = conn.cursor()
    

    try:
        response = requests.get(f"{NODE_API_URL}/sneakers", params={"keyword": sku, "limit": 1})
        response.raise_for_status()
        sneaker = response.json()[0]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Sneaks-API: {e}")
        return jsonify({"error": "Failed to fetch sneakers. Please try again later."}), 500

    average_price = 0
    resell_prices = sneaker.get('lowestResellPrice')
    if resell_prices:
        price_values = resell_prices.values()
        if price_values:
            average_price = round(sum(price_values) / len(price_values))
        else:
            average_price = None
    else:
        average_price = sneaker.get('retailPrice')

    # if average_price == -1234:
    #     average_price = sneaker.get('retailPrice')

    resell_links = sneaker.get('resellLinks', {})
    stockx_link = resell_links.get('stockX', None)
    goat_link = resell_links.get('goat', None)
    flightclub_link = resell_links.get('flightClub', None)

    sneaker_obj = Sneaker(
        resell_price=average_price,
        brand=sneaker.get('brand'),
        name=sneaker.get('shoeName'),
        price=sneaker.get('retailPrice'),
        img_url=sneaker.get('thumbnail'),
        sku=sku,
        release_date=sneaker.get('releaseDate'),
        description=sneaker.get('description'),
        stockx_link=stockx_link,
        goat_link=goat_link,
        flightclub_link=flightclub_link
    )

    print(sneaker_obj.img_url)


    discussions = logic.getSneakerDiscussions(dbCursor, sneaker_obj.sku)
    conn.close()
    
    return render_template(
        'sneakerpage.html',
        sneaker=sneaker_obj,
        discussions=discussions
    )

@app.route('/add-discussion', methods=['POST'])
def add_discussion():
    sku = request.args.get('sku')
    print(sku)
    discussion_body = request.form.get('discussion_body')
    username = session.get('username')

    if not sku:
        return "Error: Missing shoe_id", 400

    conn = get_db()
    dbCursor = conn.cursor()
    query = "INSERT INTO SneakerDiscussionEntry (Sku, Body, Username) VALUES (?, ?, ?)"
    try:
        dbCursor.execute(query, (sku, discussion_body, username))
        conn.commit()
    except Exception as e:
        print(f"Error inserting discussion: {e}")
    finally:
        conn.close()

    return redirect(url_for('sneaker_page', sku=sku))

@app.route('/add_like_sneaker_page', methods=['POST'])
def add_like_sneaker_page():
    sku = request.form.get('sku')
    discussion_id = request.form.get('discussion_id')
    username = session.get('username')

    get_likes_query = "SELECT Likes, LikedByClientUsernames FROM SneakerDiscussionEntry WHERE SneakerDiscussionEntryID = ? AND Sku = ?"
    update_likes_query = "UPDATE SneakerDiscussionEntry SET Likes = ?, LikedByClientUsernames = ? WHERE SneakerDiscussionEntryID = ? AND Sku = ?"
    
    conn = get_db()
    dbCursor = conn.cursor()

    try:
        dbCursor.execute(get_likes_query, (discussion_id, sku))
        result = dbCursor.fetchone()
        
        if result:
            current_likes = result[0]
            liked_by_clients = result[1].split(',') if result[1] else []

            if str(username) in liked_by_clients:
                liked_by_clients.remove(str(username))
                current_likes -= 1
            else:
                liked_by_clients.append(str(username))
                current_likes += 1

            updated_liked_by_clients = ','.join(liked_by_clients)
            dbCursor.execute(update_likes_query, (current_likes, updated_liked_by_clients, discussion_id, sku))
            conn.commit()

    except Exception as e:
        print(e)
    finally:
        conn.close()

    return redirect(url_for('sneaker_page', sku=sku))

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

@app.route('/add-to-collection', methods=['POST'])
def add_to_collection():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    sku = request.form.get('sku')
    name = request.form.get('name')
    brand = request.form.get('brand')
    image = request.form.get('image')
    price = request.form.get('price')

    if not sku or not name or not brand or not image or not price:
        return jsonify({'error': 'Missing required fields'}), 400

    conn = get_db()
    dbCursor = conn.cursor()

    if logic.add_to_collection(conn, dbCursor, session['username'], sku, name, brand, price, image):
        print(f"Redirecting to sneaker_page with sku: {sku}")
        return redirect(url_for('sneaker_page', sku=sku))
    else:
        return jsonify({'error': 'Failed to add to collection'}), 500

@app.route('/move-to-collection', methods=['POST'])
def move_to_collection():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    sku = request.form.get('sku')
    name = request.form.get('name')
    brand = request.form.get('brand')
    image = request.form.get('image')
    price = request.form.get('price')

    if not sku or not name or not brand or not image or not price:
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    if logic.move_to_collection(conn, dbCursor, session['username'], sku, name, brand, price, image):
        return redirect(url_for('view_wishlist'))
    else:
        return jsonify({'error': 'Failed to move to collection'}), 500

@app.route('/collection')
def view_collection():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    dbCursor = conn.cursor()
    collection_items = logic.get_collection(dbCursor, session['username'])
    
    return render_template('collection.html', items=collection_items)

@app.route('/wishlist')
def view_wishlist():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    dbCursor = conn.cursor()
    wishlist_items = logic.get_wishlist(dbCursor, session['username'])
    
    return render_template('wishlist.html', items=wishlist_items)

@app.route('/add-to-wishlist', methods=['POST'])
def add_to_wishlist():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    sku = request.form.get('sku')
    name = request.form.get('name')
    brand = request.form.get('brand')
    image = request.form.get('image')
    price = request.form.get('price')

    if not sku or not name or not brand or not image or not price:
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    if logic.add_to_wishlist(conn, dbCursor, session['username'], sku, name, brand, price, image):
        return redirect(url_for('sneaker_page', sku=sku))
    else:
        return jsonify({'error': 'Failed to add to wishlist'}), 500

@app.route('/remove-from-wishlist', methods=['POST'])
def remove_from_wishlist():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    wID = request.form.get('wishlist_id')
    if not wID:
        return jsonify({'error': 'No shoe specified'}), 400
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    if logic.remove_from_wishlist(conn, dbCursor, session['username'], wID):
        return redirect(url_for('view_wishlist'))
    else:
        return jsonify({'error': 'Failed to remove from wishlist'}), 500

def fetch_sneaker_brands():
    url = "https://v1-sneakers.p.rapidapi.com/v1/brands"
    headers = {
        "x-rapidapi-host": "v1-sneakers.p.rapidapi.com",
        "x-rapidapi-key": "8b1bac8483msh1e8e12c443cd7cbp1192cejsn4ab3a1e0147d"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        brands = response.json()
        print("Sneaker Brands:", brands)
        return brands
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"An error occurred: {err}")

@app.route('/remove-from-collection', methods=['POST'])
def remove_from_collection():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    cID = request.form.get('collection_id')
    print(cID)
    if not cID:
        return jsonify({'error': 'No shoe specified'}), 400
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    if logic.remove_from_collection(conn, dbCursor, session['username'], cID):
        return redirect(url_for('view_collection'))
    else:
        return jsonify({'error': 'Failed to remove from collection'}), 500

#Profile

@app.route('/profile/<username>')
def view_profile(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    # Get user stats (followers/following)
    user_stats = logic.get_user_stats(dbCursor, username)

    viewer = session['username']
    
    # Get user posts
    posts = logic.get_user_posts(dbCursor, username)
    
    # Get collection items
    collection_items = logic.get_collection(dbCursor, username)
    collection_count = len(collection_items)
    
    # Get wishlist items
    wishlist_items = logic.get_wishlist(dbCursor, username)
    wishlist_count = len(wishlist_items)

    is_following = logic.check_following(dbCursor, viewer, username)
    
    return render_template('profile.html',
                         user={'username': username},
                         stats=user_stats,
                         posts=posts,
                         collection_items=collection_items,
                         wishlist_items=wishlist_items,
                         collection_count=collection_count,
                         wishlist_count=wishlist_count,
                         viewer=viewer,
                         is_following=is_following)

@app.route('/save-theme', methods=['POST'])
def save_theme():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    theme = request.json.get('theme')
    if theme not in ['light', 'dark']:
        return jsonify({'error': 'Invalid theme'}), 400
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    try:
        # First, check if theme_preference column exists
        dbCursor.execute("""
            SELECT name FROM pragma_table_info('Client') 
            WHERE name='theme_preference'
        """)
        if not dbCursor.fetchone():
            # Add the column if it doesn't exist
            dbCursor.execute("""
                ALTER TABLE Client 
                ADD COLUMN theme_preference TEXT DEFAULT 'light'
            """)
        
        # Update the user's theme preference
        dbCursor.execute(
            "UPDATE Client SET theme_preference = ? WHERE Username = ?",
            (theme, session['username'])
        )
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error saving theme preference: {e}")
        return jsonify({'error': 'Database error'}), 500
    










@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))




@app.route('/get-theme')
def get_theme():
    if 'username' not in session:
        return jsonify({'theme': 'light'})
    
    conn = get_db()
    dbCursor = conn.cursor()
    
    try:
        # First, check if theme_preference column exists
        dbCursor.execute("""
            SELECT name FROM pragma_table_info('Client') 
            WHERE name='theme_preference'
        """)
        if not dbCursor.fetchone():
            return jsonify({'theme': 'light'})
        
        dbCursor.execute(
            "SELECT theme_preference FROM Client WHERE Username = ?",
            (session['username'],)
        )
        result = dbCursor.fetchone()
        theme = result[0] if result and result[0] else 'light'
        return jsonify({'theme': theme})
    except Exception as e:
        print(f"Error getting theme preference: {e}")
        return jsonify({'theme': 'light'})
    
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)