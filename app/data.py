import sqlite3

def sql_connection():
    """
    Creates a connection to SQLite database and returns the connection.
    """

    con = sqlite3.connect("chat_application.db")

    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS user 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username TEXT  NOT NULL UNIQUE,
                    password TEXT  NOT NULL)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS message 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    recipient_id INTEGER NOT NULL,
                    sender_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    type TEXT CHECK( type IN ('text','image','video') ) NOT NULL)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS text 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    message_id INTEGER NOT NULL UNIQUE,
                    data TEXT  NOT NULL)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS image 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    message_id INTEGER NOT NULL UNIQUE,
                    url TEXT  NOT NULL,
                    height INTEGER  NOT NULL,
                    width INTEGER  NOT NULL)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS video 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    message_id INTEGER NOT NULL UNIQUE,
                    url TEXT  NOT NULL,
                    source TEXT CHECK( source IN ('youtube','vimeo') ) NOT NULL)''')
    
    con.commit()  

    return con



