CREATE TABLE IF NOT EXISTS Client (
    ClientID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL,
    Password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Shoe (
    ShoeID INTEGER PRIMARY KEY AUTOINCREMENT,
    Brand TEXT,
    Name TEXT,
    AveragePrice INT,
    imgURL TEXT
);

CREATE TABLE IF NOT EXISTS Collection (
    CollectionID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientUsername TEXT NOT NULL,
    ShoeID INT NOT NULL,
    FOREIGN KEY (ClientUsername) REFERENCES Client(Username),
    FOREIGN KEY (ShoeID) REFERENCES Shoe(ShoeID)
);

CREATE TABLE IF NOT EXISTS Wishlist (
    WishlistID INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientUsername TEXT NOT NULL,
    ShoeID INT NOT NULL,
    FOREIGN KEY (ClientUsername) REFERENCES Client(Username),
    FOREIGN KEY (ShoeID) REFERENCES Shoe(ShoeID)
);

CREATE TABLE IF NOT EXISTS DiscussionEntry (
    DiscussionEntryID INTEGER PRIMARY KEY AUTOINCREMENT,
    Body TEXT,
    Username TEXT NOT NULL,
    Likes INT DEFAULT 0,
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