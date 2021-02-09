"""This module contains configuration variables."""

from environs import Env

env = Env()
env.read_env()


TOKEN = env("TOKEN")
GROUP_CHANNEL_ID = env("GROUP_CHANNEL_ID")
TRACKLIST_NAME = "tracklist.txt"
DATABASE_NAME = "tracklist.db"
