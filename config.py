"""This module contains configuration variables."""
import database

TOKEN = "1313099557:AAGvmoZWP85GRKrLpjldczj0PZZHxi-fCTo"
TRACKLIST_NAME = "tracklist.txt"
DATABASE_NAME = "tracklist.db"
GROUP_CHANNEL_ID = '@testchannel2111'

db = database.Database(DATABASE_NAME)
AUTHOR_KEYBOARD, SONG_KEYBOARD = db.get_keyboards()
db.close()
