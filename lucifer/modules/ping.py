import html
import json
import random
import time
import pyowm
from pyowm import timeutils, exceptions
from datetime import datetime
from typing import Optional, List

import requests
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram import Update, Bot
from telegram.ext import run_async

from lucifer.modules.disable import DisableAbleCommandHandler
from lucifer import dispatcher
import lucifer.modules.helper_funcs.memes_strings as memes_strings

from requests import get


@run_async
def ping(update, context):
    start_time = time.time()
    requests.get('https://api.telegram.org')
    end_time = time.time()
    ms = float(end_time - start_time)
    update.effective_message.reply_text("random.choice(memes_strings.PING_STRING)\n⏱️Reply took: {0:.2f}s".format(round(ms, 2) % 60), parse_mode=ParseMode.MARKDOWN)



PING_HANDLER = DisableAbleCommandHandler("ping", ping)

dispatcher.add_handler(PING_HANDLER)

__command_list__ = ["ping"]
__handlers__= [PING_HANDLER]
