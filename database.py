"""This module works with database(DB)."""

import sqlite3
import re
from os.path import exists

from config import DATABASE_NAME, TRACKLIST_NAME

from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    fn
)

dbase = SqliteDatabase(DATABASE_NAME)


class Tracklist(Model):

    author = CharField()
    song = CharField()

    class Meta:
        database = dbase
        db_table = 'tracklist'


def load_tracklist_from_file(filename):
    """Load new tracklist from file to DB.

    :param filename: (str) Tracklist filename
    """
    sep, tracklist = ' - ', []
    with open(filename, encoding='utf-8-sig') as f:
        for line in f:
            line = re.sub(r'\d+\. ', '', line)
            author_song = line.rstrip().split(sep=sep)
            # read pair "author - song title"
            tracklist.append(tuple(author_song))
    # save first letters of authors and songs
    Tracklist.drop_table()
    Tracklist.create_table()
    Tracklist.insert_many(
        tracklist, fields=[Tracklist.author, Tracklist.song]).execute()


def get_keyboards() -> tuple:
    """Return first letters of authors and songnames.

    :return: ((list) author_1st_letters, (list) song_1st_letters)
    """
    author_letters = (Tracklist
                      .select(fn.substr(Tracklist.author, 1, 1)
                              .alias('letter'))
                      .distinct()
                      .order_by(Tracklist.author))
    song_letters = (Tracklist
                    .select(fn.substr(Tracklist.song, 1, 1)
                            .alias('letter'))
                    .distinct()
                    .order_by(Tracklist.song))
    author_keyboard = [a_let.letter for a_let in author_letters]
    song_keyboard = [s_let.letter for s_let in song_letters]
    return author_keyboard, song_keyboard


def select_field_by_letter(letter: str, field: str) -> list:
    """Return list of authors or songs, which names starts with letter.

    :param letter: (str) 1st letter in author or song name
    :param field: (str) field in database which you want to filter (author
    or song)
    :return: (list) List of authors or songs
    """
    # Working with rows as dictionaries, because it will make it easier
    # to retrieve the data through query
    #
    # getattr(Tracklist, field)) == Tracklist.author or Tracklist.song,
    # depending on the parameter field
    query = (Tracklist
             .select()
             .distinct()
             .where(fn.upper(getattr(Tracklist, field)) % f'{letter.upper()}%')
             .dicts())
    data = [item[field] for item in query]
    return data


def select_pair(field: str, item: str) -> list:
    """Return pair (author, song) from database, filtered by desired field.

    :param field: (str) field in DB to be selected
    :param item: (str) author or song in DB
    :return: (list) List of tuples (author, song)
    """
    query = (Tracklist
             .select()
             .where(getattr(Tracklist, field) == item))
    data = [(obj.author, obj.song) for obj in query]
    return data


class Database:
    """Database class."""

    def __init__(self, database):
        """Initialise connection with DB."""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        try:
            self.AUTHOR_KEYBOARD, self.SONG_KEYBOARD = self.get_keyboards()

        except sqlite3.OperationalError:
            if exists(TRACKLIST_NAME):
                self.load_tracklist_from_file(TRACKLIST_NAME)
                self.AUTHOR_KEYBOARD, self.SONG_KEYBOARD = self.get_keyboards()
            else:
                print("Load tracklist!")

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

    def close(self):
        """Close connection with database."""
        self.connection.close()


AUTHOR_KEYBOARD, SONG_KEYBOARD = get_keyboards()
