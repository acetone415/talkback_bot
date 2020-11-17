import sqlite3
import re
import config


class Database:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def load_tracklist_from_file(self, filename):
        sep, tracklist = ' - ', []
        with open(filename, encoding='utf-8-sig') as f:  # utf-
            for line in f:
                line = re.sub(r'\d+\. ', '', line)
                tracklist.append(tuple(line.rstrip().split(sep=sep)))  # read pair "author - song title"
        self.cursor.executemany("INSERT INTO tracklist (artist_name, song_name) VALUES (?, ?);", tracklist)
        self.connection.commit()

db = Database(config.DATABASE_NAME)
db.load_tracklist_from_file(config.TRACKLIST_NAME)




