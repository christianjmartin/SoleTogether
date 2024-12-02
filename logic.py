from datetime import datetime 

def signup(conn, dbCursor, username, password):
    checkExists = "SELECT * FROM Client WHERE Username = ?"
    dbCursor.execute(checkExists, (username,))
    duplicate = dbCursor.fetchone()
    if duplicate:
        return False
    query = "INSERT INTO Client (Username, Password) VALUES (?, ?)"
    try:
        dbCursor.execute(query, (username, password))
        conn.commit()
        return True
    except Exception as e:
        print(e)
        return False

def login(dbCursor, username, password):
    checkExists = "SELECT * FROM Client WHERE Username = ? AND Password = ?"
    dbCursor.execute(checkExists, (username, password))
    good = dbCursor.fetchone()
    if good is not None:
        return True
    else:
        return False
    
def create_discussion_entry(conn, dbCursor, username, body):
    """Create a new discussion entry"""
    query = "INSERT INTO DiscussionEntry (Body, Username) VALUES (?, ?)"
    try:
        dbCursor.execute(query, (body, username))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating discussion entry: {e}")
        return False

def get_discussion_entries(dbCursor, limit=50):
    """Get all discussion entries, ordered by most recent first"""
    query = """
        SELECT de.DiscussionEntryID, de.Body, de.Username, de.Likes, 
               COUNT(DISTINCT f.FollowerUsername) as FollowerCount
        FROM DiscussionEntry de
        LEFT JOIN Follows f ON de.Username = f.FollowingUsername
        GROUP BY de.DiscussionEntryID
        ORDER BY de.DiscussionEntryID DESC
        LIMIT ?
    """
    try:
        dbCursor.execute(query, (limit,))
        return dbCursor.fetchall()
    except Exception as e:
        print(f"Error fetching discussion entries: {e}")
        return []

def toggle_like(conn, dbCursor, client_id, entry_id):
    """Toggle like status for a discussion entry"""
    try:
        # Check if like exists
        check_query = "SELECT LikesID FROM Likes WHERE ClientID = ? AND DiscussionEntryID = ?"
        dbCursor.execute(check_query, (client_id, entry_id))
        existing_like = dbCursor.fetchone()

        if existing_like:
            # Unlike: Remove like and decrease count
            delete_query = "DELETE FROM Likes WHERE ClientID = ? AND DiscussionEntryID = ?"
            update_query = "UPDATE DiscussionEntry SET Likes = Likes - 1 WHERE DiscussionEntryID = ?"
            dbCursor.execute(delete_query, (client_id, entry_id))
            dbCursor.execute(update_query, (entry_id,))
        else:
            # Like: Add like and increase count
            insert_query = "INSERT INTO Likes (ClientID, DiscussionEntryID) VALUES (?, ?)"
            update_query = "UPDATE DiscussionEntry SET Likes = Likes + 1 WHERE DiscussionEntryID = ?"
            dbCursor.execute(insert_query, (client_id, entry_id))
            dbCursor.execute(update_query, (entry_id,))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling like: {e}")
        return False
    

def check_following(dbCursor, follower_username, following_username):
    try:
        # Check if already following
        check_query = """
            SELECT * FROM Follows 
            WHERE FollowerUsername = ? AND FollowingUsername = ?
        """
        dbCursor.execute(check_query, (follower_username, following_username))
        existing_follow = dbCursor.fetchone()

        if existing_follow:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking following status: {e}")
        return False

def toggle_follow(conn, dbCursor, follower_username, following_username):
    """Toggle follow status for a user"""
    try:
        # Check if already following
        check_query = """
            SELECT * FROM Follows 
            WHERE FollowerUsername = ? AND FollowingUsername = ?
        """
        dbCursor.execute(check_query, (follower_username, following_username))
        existing_follow = dbCursor.fetchone()

        if existing_follow:
            # Unfollow
            delete_query = """
                DELETE FROM Follows 
                WHERE FollowerUsername = ? AND FollowingUsername = ?
            """
            dbCursor.execute(delete_query, (follower_username, following_username))
        else:
            # Follow
            insert_query = """
                INSERT INTO Follows (FollowerUsername, FollowingUsername) 
                VALUES (?, ?)
            """
            dbCursor.execute(insert_query, (follower_username, following_username))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error toggling follow: {e}")
        return False

def get_user_stats(dbCursor, username):
    """Get a user's follower and following counts"""
    try:
        # Get follower count
        follower_query = """
            SELECT COUNT(*) FROM Follows 
            WHERE FollowingUsername = ?
        """
        dbCursor.execute(follower_query, (username,))
        follower_count = dbCursor.fetchone()[0]

        # Get following count
        following_query = """
            SELECT COUNT(*) FROM Follows 
            WHERE FollowerUsername = ?
        """
        dbCursor.execute(following_query, (username,))
        following_count = dbCursor.fetchone()[0]

        return {
            'followers': follower_count,
            'following': following_count
        }
    except Exception as e:
        print(f"Error getting user stats: {e}")
        return {'followers': 0, 'following': 0}
    

def getSneakerDiscussions(dbCursor, sku):
    # getShoe = "SELECT ShoeID FROM Shoe WHERE sku=?"

    # try:
    #     dbCursor.execute(getShoe, (sku))
    #     shoe_row = dbCursor.fetchone()
    #     if shoe_row is None:
    #         print("No matching ShoeID found.")
    #         return [] 
    #     sku = shoe_row[0]
    # except Exception as e:
    #     print(f"Error fetching ShoeID: {e}")
    #     return []
    
    query = "SELECT SneakerDiscussionEntryID, Username, Body, EntryDate, Likes FROM SneakerDiscussionEntry WHERE Sku = ? ORDER BY EntryDate DESC"
    try:
        dbCursor.execute(query, (sku,))
        results = dbCursor.fetchall()
        
        discussions = []
        for row in results:
            entry_date = row[3]
            if isinstance(entry_date, str):
                entry_date = datetime.strptime(entry_date, "%Y-%m-%d %H:%M:%S").date()
            elif isinstance(entry_date, datetime):
                entry_date = entry_date.date()
            discussions.append({
                'discussion_id': row[0],
                'Username': row[1],
                'Body': row[2],
                'EntryDate': entry_date,
                'Likes': row[4]
            })
        return discussions

    except Exception as e:
        print(f"Error fetching discussions: {e}")
        return []
   

def add_to_collection(conn, dbCursor, username, sku, name, brand, price, image):
    try:
        query = "INSERT INTO Collection (ClientUsername, Sku, Brand, Name, ResellPrice, ImageURL) VALUES (?, ?, ?, ?, ?, ?)"
        dbCursor.execute(query, (username, sku, brand, name, price, image))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding to collection: {e}")
        return False

def get_collection(dbCursor, username):
    query = "SELECT CollectionID, Sku, Brand, Name, ResellPrice, ImageURL FROM Collection WHERE ClientUsername = ? ORDER BY CollectionID DESC"
    try:
        dbCursor.execute(query, (username,))
        return dbCursor.fetchall()
    except Exception as e:
        print(f"Error fetching collection: {e}")
        return []

def move_to_collection(conn, dbCursor, username, sku, name, brand, price, image):
    try:
        # Remove from wishlist
        remove_query = "DELETE FROM Wishlist WHERE ClientUsername = ? AND Sku = ?"
        dbCursor.execute(remove_query, (username, sku))
        
        # Add to collection
        add_query = "INSERT INTO Collection (ClientUsername, Sku, Brand, Name, ResellPrice, ImageURL) VALUES (?, ?, ?, ?, ?, ?)"
        dbCursor.execute(add_query, (username, sku, brand, name, price, image))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"Error moving to collection: {e}")
        return False

def add_to_wishlist(conn, dbCursor, username, sku, name, brand, price, image):
    try:
        # Check if shoe already exists in wishlist
        check_query = "SELECT * FROM Wishlist WHERE ClientUsername = ? AND Sku = ?"
        dbCursor.execute(check_query, (username, sku))
        if dbCursor.fetchone():
            return True  # Item already in wishlist
            
        query = "INSERT INTO Wishlist (ClientUsername, Sku, Brand, Name, ResellPrice, ImageURL) VALUES (?, ?, ?, ?, ?, ?)"
        dbCursor.execute(query, (username, sku, brand, name, price, image))
        conn.commit()
        return True
    
    except Exception as e:
        print(f"Error adding to collection: {e}")
        return False
    

def get_wishlist(dbCursor, username):
    query = "SELECT WishlistID, Sku, Brand, Name, ResellPrice, ImageURL FROM Wishlist WHERE ClientUsername = ? ORDER BY WishlistID DESC"
    try:
        dbCursor.execute(query, (username,))
        return dbCursor.fetchall()
    except Exception as e:
        print(f"Error fetching wishlist: {e}")
        return []

def remove_from_wishlist(conn, dbCursor, username, wID):
    try:
        query = "DELETE FROM Wishlist WHERE ClientUsername = ? AND WishlistID = ?"
        dbCursor.execute(query, (username, wID))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error removing from wishlist: {e}")
        return False
    
def remove_from_collection(conn, dbCursor, username, sku):
    try:
        query = "DELETE FROM Collection WHERE ClientUsername = ? AND CollectionID = ?"
        dbCursor.execute(query, (username, sku))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error removing from collection: {e}")
        return False
    
#Profile Pic
def get_user_posts(dbCursor, username):
    """Get all posts by a user (both general and sneaker discussions)"""
    query = """
        SELECT 'Discussion' as type, Body, Username, Likes, 
               datetime('now') as PostDate
        FROM DiscussionEntry
        WHERE Username = ?
        UNION ALL
        SELECT 'Sneaker' as type, Body, Username, Likes, 
               EntryDate as PostDate
        FROM SneakerDiscussionEntry
        WHERE Username = ?
        ORDER BY PostDate DESC
    """
    try:
        dbCursor.execute(query, (username, username))
        posts = dbCursor.fetchall()
        return [{
            'type': post[0],
            'body': post[1],
            'likes': post[3],
            'date': post[4]
        } for post in posts]
    except Exception as e:
        print(f"Error fetching user posts: {e}")
        return []

def get_followers(dbCursor, username):
    """Get users following this user"""
    query = """
        SELECT FollowerUsername, DateFollowed
        FROM Follows
        WHERE FollowingUsername = ?
        ORDER BY DateFollowed DESC
    """
    try:
        dbCursor.execute(query, (username,))
        followers = dbCursor.fetchall()
        return [{
            'username': follower[0],
            'date_followed': follower[1]
        } for follower in followers]
    except Exception as e:
        print(f"Error fetching followers: {e}")
        return []

def get_following(dbCursor, username):
    """Get users this user is following"""
    query = """
        SELECT FollowingUsername, DateFollowed
        FROM Follows
        WHERE FollowerUsername = ?
        ORDER BY DateFollowed DESC
    """
    try:
        dbCursor.execute(query, (username,))
        following = dbCursor.fetchall()
        return [{
            'username': following[0],
            'date_followed': following[1]
        } for following in following]
    except Exception as e:
        print(f"Error fetching following: {e}")
        return []
    


def insert_brands(conn, dbCursor, username, brands):
    try:
        check = "SELECT * FROM UserBrands WHERE ClientUsername = ?"
        dbCursor.execute(check, (username,))
        result = dbCursor.fetchone()
        if result != None:
            reset = "DELETE FROM UserBrands WHERE ClientUsername = ?"
            dbCursor.execute(reset, (username,))
            conn.commit()
            for brand in brands:
                query = "INSERT INTO UserBrands (ClientUsername, brands) VALUES (?,?)"
                dbCursor.execute(query, (username, brand))
        else:   
            for brand in brands:
                query = "INSERT INTO UserBrands (ClientUsername, brands) VALUES (?,?)"
                dbCursor.execute(query, (username, brand))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding to collection: {e}")
        return False
    
def get_user_brands(dbCursor, username):
    try:
        query = "SELECT brands FROM UserBrands WHERE ClientUsername = ?"
        dbCursor.execute(query, (username,))
        result = dbCursor.fetchall()
        brands = [row[0] for row in result] if result else []
        return brands
    except Exception as e:
        print(f"Error adding to collection: {e}")
        return False