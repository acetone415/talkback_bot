# talkback_bot

## Description
This bot allows to send next song from your tracklist to the group chat.
This bot based on [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI).


## How to run

* Clone the code from this repository
* Fill _.env_ file (.env.example as example):
  * First, you'll need a Telegram Bot Token, you can get it via BotFather 
([more info here](https://core.telegram.org/bots)).  
  * Enter your Token in _.env_:
  > TOKEN = "Token_From_BotFather"
  * Create channel in Telegram, where Bot will send next songs in Telegram and make your Bot an administrator in this Channel
  * Enter channel name in _.env_:
  > GROUP_CHANNEL_ID = "@your_channel_id"
* pip install -r requirements.txt
* Run _main.py_
