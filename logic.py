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
