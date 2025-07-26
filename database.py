import sqlite3
from contextlib import closing

def get_db():
    return sqlite3.connect('data/senatai.db')

def init_db():
    with closing(get_db()) as db:
        with open('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
