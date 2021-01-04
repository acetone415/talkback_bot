"""This module contains configuration variables."""

from environs import Env


env = Env()
env.read_env()


TOKEN = env("TOKEN")
GROUP_CHANNEL_ID = env("GROUP_CHANNEL_ID")
TRACKLIST_NAME = "tracklist.txt"
DATABASE_NAME = "tracklist.db"
HELP_INFO = """Для того, чтобы перейти к выбору песни, введите любой символ
Для обновления треклиста просто загрузите его"""
