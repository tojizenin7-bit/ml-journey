#storage.py - database layer for lifelog
# this file will handle all rhe communicaaion with the SQLite database
#repository pattern is called keeping all database logic in one place

import sqlite3 #built in python library for working with SQLite databases
import os #for working with file paths
from datetime import datetime #to store timestamps with every entry


#CONSTANT - the database filename
#writing it here once means if we ever need. to rename it, we only have to change it in one place

#ALL_CAPS is the python convention for constants

DB_file = "lifelog.db"

def get_connection():
    """ opens or creates the SQlite database and returns a connection object.
    SQLite stores your entire database as a single .db file on disk.
    when you call sqlite3.connect("lifelog.db"):
    - if the file exists -> it opens it.
    -if it doesnt exist -> it creates it automatically.    
    the connection object is like a "phone line " to your database.
    you send it SQL commands and it returns results.
"""
    conn = sqlite3.connect( DB_file )

# this one line makes SQLite to return rows as dicrionary like objectsinstead of tupules
#so we can access columns by name:  row["mood"] instead of row[0].
#row factories are a feature of the sqlite3 library that allow you to customize how rows are returned from the database.conn.row_factory = sqlite3.Row
    conn.row_factory = sqlite3.Row
    return conn
def init_db():
    """creates the database tables if they dont exist already.
    Call this once at startup in (cli.py) to setup the schema.
    schema means the structure of your database- what tables exsist and what columns each table has."""
    
    # with statement is a context manager that automatically closes the connection when we're done with it, even if an error occurs.)
    # this prevents connection bugs- always use with for DB connections.
    
    with get_connection() as conn:
        
        #conn.execute() sends a SQL command to the database.
        #triple quoted strings (""" """) allow us to write multi line SQL commands for better readability.
        conn.execute("""
                     
            CREATE TABLE IF NOT EXISTS entries (
            
                id          INTEGER  PRIMARY KEY ANNOUNCEMENT,
                date        TEXT   NOT NULL UNIQUE,
                mood.       INTEGER NOT NULL,
                energy      INTEGER NOT NULL,
                note        TEXT,
                created_at  TEXT NOT NULL    )
                """)
        # explanaition of each column:
        # id - auto incrementing number, uniquely identifies each row
        # #date - stored as YYYY-MM-DD text (eg "2024-06-01")
        #mood - integer 1-10
        #energy - integer 1-10
        #note - free texxt, can be empty (no NOT NULL constraint)
        #created_at - timestamp of when the entry was created
        #UNIQUE on date means upi cant log on the same day twice
        conn.execute("""
                    CREATE TABLE IF NOT EXISTS habits (

                        id         INTEGER PRIMARY KEY ANNOUNCEMENT,
                        entry_id   INTEGER NOT NULL,
                        name.      TEXT NOT NULL,
                        done.      INTEGER NOT NULL,
                        FOREIGN KEY (entry_id) REFERENCES entries (id)
                        )
                    """)
        #explanation
        #id - auto incrementing number, uniquely identifies each row
        #entry_id - links this habit to a specific entry in the entries table (foreign key
        #name - habit name (eg "exercise", "meditation")
        #done - SQLITE has no boolean type; we use 0=false, 1=true
        #FOREIGN KEY constraint ensures that entry_id must exist in the entries table
        # with sqlite3 you must commit changes  to save them to database
        conn.commit()

        print("database ready.")
def save_entry(date: str, mood: int, energy: int, note: str, habits: dict):
    """
    inserts a new daily log entry + its habits into the database.
    
    Parameters:
        date   -  "YYYY-MM-DD" format string
        mood   -  integer 1-10
        energy -  integer 1-10
        note   -  free text string(can be empty)
        habits -  dict like {"exercise": True, "meditation": False}
    
    type hints(the' : str' , ': int' parts) dont enforce types at runtime ,but they act as documentation and help VScode autocomplete correctly.
        """            
    created_at =datetime.now().isoformat()
    #datetime.now() current date and time as object
    # isoformat() converts it to a string like "2024-06-01T14:30:00"

    with get_connection() as conn:
    #--INSERT the main entry row into the entries table
    # #the ? are placeholders for parameters to prevent SQL injection attacks
    # sql replaces the ? with the values from the tuple (date, mood, energy, note, created_at) safely.
        cursor = conn.execute("""
                    INSERT INTO entries (date, mood, energy, note, created_at) 
                    VALUES (?, ?, ?, ?, ?)
                    """, (date, mood, energy, note, created_at))
    #cursor.lastrowid gives us the autogenrated id of row we just inserted.
    #we need it to link the habits rowsback to this entry.
    entry_id = cursor.lastrowid

    #--INSERT habits into the habits table
    #habit items return pairs like ("exercise", True)
    for habit_name, done in habits.items():
        conn.execute("""
                    INSERT INTO habits (entry_id, name, done)
                    VALUES (?, ?, ?)
                    """, (entry_id, habit_name, int(done)))
    #int(is_done) converts True to 1 and False to 0 for sqlite storage

    conn.commit()
    print(f"Entry for {date} saved successfully.")

def fetch_all_entries():
    """
    returns all entries from the database as a list of row objects.
    this is used by analyzer and dashboard to get full. dataset
    each row object behaves like a dictionary with column names as keys 
    
    example:
    entires = fetch_all_entries()
    for e in entriies:
        print (e["mood"])
        #prints the mood column of each entry"""
    
    with get_connection() as conn:
        #order by date ASC returns rows from oldest to newest.
        #this isimportant for time series analysis in the analyzer module.
        cursor = conn.execute("SELECT* FROM entries ORDER BY date ASC")
        return cursor.fetchall()
    #fetchall() returns a python list of all rows

def fetch_habits_for_entry(entry_id: int):
    """
    returns all habit rows linked to a specific entry_id.
    """
    with get_connection() as conn:
        cursor = conn.execute(
        "SELECT *FROM habits WHERE entry_id = ?", (entry_id,)
        )
        #note the trailing comma in (entry_id,) - this makes it a tupule with one element, which is required by the sqlite parameter substitution syntax.
        # #sqlite3 requires parameters as a tupule or list not a bare value.
        return cursor.fetchall()

def fetch_entry_by_date(date: str):
    """
    returns a single entry row matching the given date, or None if no entry exists for that date.
    this is used by cli.py to check if user is trying to log on a date that already has an entry (remember we have UNIQUE constraint on date column)
    """
    with get_connection() as conn:
        cursor = conn.execute(
        "SELECT * FROM entries WHERE date = ?", (date,)
        )
        return cursor.fetchone()
    #fetchone() returns a single row or None 

def fetch_recent_entries(n: int =7 ):
    """
    returns the most recent n entries (default 7 = last week).
    default parameter values (n=7) are great for convinience-
    callers can write fetch_recent_entries() or fetch_recent_entries(30)."""            
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT * FROM entries ORDER BY date DESC LIMIT ?",(n,)
        )
        #we reverse so the list goes oldest -> newest(better for charts).
        return
    list(reversed(cursor.fetchall()))