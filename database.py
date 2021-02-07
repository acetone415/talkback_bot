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
             .select(getattr(Tracklist, field))
             .distinct()
             .where(getattr(Tracklist, field) ** f'{letter.upper()}%')
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


AUTHOR_KEYBOARD, SONG_KEYBOARD = get_keyboards()
