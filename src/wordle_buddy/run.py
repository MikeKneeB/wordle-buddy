#!/usr/bin/env python


import os

from dotenv import load_dotenv
from wordle_buddy.json_db import JsonWordleDB
from wordle_buddy.connect import WordleClient
from wordle_buddy.message import WordleMessageManager
from wordle_buddy.commands import WordleCommandHandler
from emoji import emojize


def run_buddy():
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    watch_channel = emojize(os.getenv('WATCH_CHANNEL'))
    print(watch_channel)
    results_directory = os.getenv('RESULTS_DIRECTORY')

    db = JsonWordleDB(results_directory)
    manager = WordleMessageManager(db)
    commands = WordleCommandHandler(db)
    client = WordleClient(watch_channel, manager, commands)

    client.run(token)


if __name__ == '__main__':
    run_buddy()
