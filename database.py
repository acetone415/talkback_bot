"""This module works with database"""

import sqlite3
import re
import config


class Database:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def create_table(self):
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tracklist (
                                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                                "author" TEXT,
                                "song" TEXT);""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS keyboards (
                                        "song_first_letters" TEXT,
                                        "author_first_letters" TEXT);""")
        self.connection.commit()

    def drop_table(self):
        self.cursor.execute("""DROP TABLE IF EXISTS tracklist;""")
        self.cursor.execute("""DROP TABLE IF EXISTS keyboards;""")
        self.connection.commit()

    def load_tracklist_from_file(self, filename):
        """Load new tracklist from file to database

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
        self.drop_table()
        self.create_table()
        self.cursor.executemany("""INSERT INTO tracklist(author, song)
                                    VALUES (?, ?);""", tracklist)
        self.cursor.execute("INSERT INTO keyboards VALUES (?, ?);",
                            (author_1st_letters.upper(),
                             song_1st_letters.upper()))
        self.connection.commit()

    def get_keyboards(self) -> tuple:
        """Returns first letters of authors and songnames

        :return: (tuple) ((str) author_1st_letters,
                          (str) song_1st_letters)
        """
        self.cursor.execute("SELECT * FROM keyboards")
        row = self.cursor.fetchone()
        author_1st_letters = row[0]
        song_1st_letters = row[1]
        return author_1st_letters, song_1st_letters

    def select_authors(self, letter: str):
        """Return list of authors, which names starts with letter

        :param letter: (str) 1st letter in author name
        :return: (list) List of authors
        """
        self.cursor.execute(f"""SELECT author FROM tracklist
                                WHERE author LIKE '{letter.upper()}%';""")
        return self.cursor.fetchall()

    def close(self):
        """Close connection with database"""
        self.connection.close()

