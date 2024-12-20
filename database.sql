CREATE TABLE IF NOT EXISTS Client (
    ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Password TEXT NOT NULL,
    theme_preference TEXT DEFAULT 'light'
);

-- CREATE TABLE IF NOT EXISTS Shoe (
--     ShoeID INTEGER PRIMARY KEY AUTOINCREMENT,
--     Brand TEXT,
--     Name TEXT,
--     AveragePrice INT,
--     imgURL TEXT
-- );

CREATE TABLE IF NOT EXISTS Collection (
    CollectionID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientUsername TEXT NOT NULL,
    Sku TEXT NOT NULL,
    Brand TEXT NOT NULL,
    Name TEXT NOT NULL,
    ResellPrice TEXT NOT NULL,
    ImageURL TEXT NOT NULL,
    FOREIGN KEY (ClientUsername) REFERENCES Client(Username)
);

CREATE TABLE IF NOT EXISTS Wishlist (
    WishlistID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientUsername TEXT NOT NULL,
    Sku TEXT NOT NULL,
    Brand TEXT NOT NULL,
    Name TEXT NOT NULL,
    ResellPrice TEXT NOT NULL,
    ImageURL TEXT NOT NULL,
    FOREIGN KEY (ClientUsername) REFERENCES Client(Username)
);

CREATE TABLE IF NOT EXISTS DiscussionEntry (
    DiscussionEntryID INTEGER PRIMARY KEY AUTOINCREMENT,
    Body TEXT,
    Username TEXT NOT NULL,
    Likes INT DEFAULT 0,
    FOREIGN KEY (Username) REFERENCES Client(Username)
);

CREATE TABLE IF NOT EXISTS SneakerDiscussionEntry (
    SneakerDiscussionEntryID INTEGER PRIMARY KEY AUTOINCREMENT,
    Sku TEXT NOT NULL,
    Body TEXT,
    Username TEXT NOT NULL,
    Likes INT DEFAULT 0,
    EntryDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    LikedByClientUsernames TEXT DEFAULT '',
    FOREIGN KEY (Username) REFERENCES Client(Username)
);

CREATE TABLE IF NOT EXISTS Likes (
    LikesID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientID INT REFERENCES Client(ClientID),
    DiscussionEntryID INT REFERENCES DiscussionEntry(DiscussionEntryID),
    LikeDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Follows (
    FollowerUsername TEXT NOT NULL,
    FollowingUsername TEXT NOT NULL,
    DateFollowed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (FollowerUsername, FollowingUsername),
    FOREIGN KEY (FollowerUsername) REFERENCES Client(Username),
    FOREIGN KEY (FollowingUsername) REFERENCES Client(Username)
);


CREATE TABLE IF NOT EXISTS UserBrands (
    ClientUsername TEXT,
    brands TEXT,
    FOREIGN KEY (ClientUsername) REFERENCES Client(Username)
);