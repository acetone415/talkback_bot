"""This module works with database(DB)."""

import sqlite3
import re
from os.path import exists

from config import DATABASE_NAME, TRACKLIST_NAME


class Database:
    """Database class."""

    def __init__(self, database):
        """Initialise connection with DB."""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        """Create tables tracklist and keyboards from DB.

        Table 'tracklist' contains authors and song names.
        Table 'keyboards' contains first letters of author names and song names.
        """
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tracklist (
                                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                                "author" TEXT,
                                "song" TEXT);""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS keyboards (
                                        "song_first_letters" TEXT,
                                        "author_first_letters" TEXT);""")
        self.connection.commit()

    def drop_tables(self):
        """Drop tables tracklist and keyboards from DB."""
        self.cursor.execute("""DROP TABLE IF EXISTS tracklist;""")
        self.cursor.execute("""DROP TABLE IF EXISTS keyboards;""")
        self.connection.commit()

    def load_tracklist_from_file(self, filename):
        """Load new tracklist from file to DB.

        :param filename: (str) Tracklist filename
        """
        sep, tracklist = ' - ', []
        song_1st_letters, author_1st_letters = [], []
        with open(filename, encoding='utf-8-sig') as f:
            for line in f:
                line = re.sub(r'\d+\. ', '', line)
                author_song = line.rstrip().split(sep=sep)
                author_1st_letters.append(author_song[0][0])
                song_1st_letters.append(author_song[1][0])
                # read pair "author - song title"
                tracklist.append(tuple(author_song))
        # save first letters of authors and songs
        author_1st_letters = ''.join(sorted(list(set(author_1st_letters))))
        song_1st_letters = ''.join(sorted(list(set(song_1st_letters))))
        self.drop_tables()
        self.create_tables()
        self.cursor.executemany("""INSERT INTO tracklist(author, song)
                                    VALUES (?, ?);""", tracklist)
        self.cursor.execute("INSERT INTO keyboards VALUES (?, ?);",
                            (author_1st_letters.upper(),
                             song_1st_letters.upper()))
        self.connection.commit()

    def get_keyboards(self) -> tuple:
        """Return first letters of authors and songnames.

        :return: (tuple) ((str) author_1st_letters,
                          (str) song_1st_letters)
        """
        self.cursor.execute("SELECT * FROM keyboards")
        row = self.cursor.fetchone()
        author_1st_letters = row[0]
        song_1st_letters = row[1]
        return author_1st_letters, song_1st_letters

    def select_field_by_letter(self, letter: str, field: str) -> list:
        """Return list of authors or songs, which names starts with letter.

        :param letter: (str) 1st letter in author or song name
        :param field: (str) field in database which you want to filter (author
        or song)
        :return: (list) List of authors or songs
        """
        self.cursor.execute(f"""SELECT DISTINCT {field} FROM tracklist
                                WHERE {field} LIKE '{letter.upper()}%';""")
        return self.cursor.fetchall()

    def select_pair(self, field: str, item: str) -> list:
        """Return pair (author, song) from database, filtered by desired field.

        :param field: (str) field in DB to be selected
        :param item: (str) author or song in DB
        :return: (list) List of tuples (author, song)
        """
        self.cursor.execute(f"""SELECT author, song FROM tracklist
                                   WHERE {field} = '{item}';""")
        return self.cursor.fetchall()

    def check_tables_existense(self):
        """Check the existence of tables 'tracklist' and 'keyboards' in the DB."""
        self.cursor.execute("""SELECT count(*) FROM sqlite_master
                                WHERE type='table'
                                AND name in ('tracklist', 'keyboards');
                            """)
        if self.cursor.fetchone()[0] == 2:
            return True
        return False

    def close(self):
        """Close connection with database."""
        self.connection.close()


try:
    db = Database(DATABASE_NAME)
    AUTHOR_KEYBOARD, SONG_KEYBOARD = db.get_keyboards()
    db.close()
except sqlite3.OperationalError:
    if exists(f'{TRACKLIST_NAME}'):
        db = Database(DATABASE_NAME)
        db.load_tracklist_from_file(f"{TRACKLIST_NAME}")
        AUTHOR_KEYBOARD, SONG_KEYBOARD = db.get_keyboards()
        db.close()
    else:
        AUTHOR_KEYBOARD, SONG_KEYBOARD = [], []
        print("Error! There is no tracklist file!")
