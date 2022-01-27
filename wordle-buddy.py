#!/usr/bin/env python


import os

from dotenv import load_dotenv
from core.json_db import JsonWordleDB
from core.wconnect import WordleClient
from core.wmessage import WordleMessageManager
from core.wcommands import WordleCommandHandler


if __name__ == '__main__':
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    watch_channel = os.getenv('WATCH_CHANNEL')
    results_directory = os.getenv('RESULTS_DIRECTORY')

    db = JsonWordleDB(results_directory)
    manager = WordleMessageManager(db)
    commands = WordleCommandHandler(db)
    client = WordleClient(watch_channel, manager, commands)

    client.run(token)
