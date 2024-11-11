import os 
import sqlite3

conn = sqlite3.connect('database.db')
dbCursor = conn.cursor()

shoes = [
    ("Nike", "Nike Calm Mule", 60, "/static/calm.jpeg"),
    ("Adidas", "Adidas Yeezy Boost 350 Turtle Dove", 375, "/static/dove.jpeg"),
    ("Nike", "Nike Dunk Retro High SE", 100, "/static/grDunk.jpeg"),
    ("Jordan", "Nike Air Jordan 4 Eminem", 22000, "/static/eminem.jpeg"),
    ("Nike", "Nike Foamposite Lite Kryptonate", 3300, "/static/kryp.jpeg"),
    ("Adidas", "Adidas Samba Messi", 150, "/static/messi.jpeg"),
    ("Nike", "Nike Dunk Low SB Paris", 45000, "/static/paris.jpeg"),
    ("Nike", "Nike Dunk Low SB What The", 17000, "/static/whatthe.jpeg")
]

for brand, name, price, img_url in shoes:
    dbCursor.execute("INSERT INTO Shoe (Brand, Name, AveragePrice, imgURL) VALUES (?, ?, ?, ?)", (brand, name, price, img_url))

conn.commit()
conn.close()