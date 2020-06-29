import html
import json
import os
import psutil
import random
import time
import datetime
from typing import Optional, List
import re
import requests
from telegram.error import BadRequest
import lucifer.modules.helper_funcs.cas_api as cas
from telegram import Message, Chat, Update, Bot, MessageEntity
from telegram import ParseMode
from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html
from lucifer.modules.helper_funcs.chat_status import user_admin, is_user_admin
from lucifer import dispatcher, OWNER_ID, SUDO_USERS, SUPPORT_USERS, WHITELIST_USERS, DEV_USERS
from lucifer.__main__ import STATS, USER_INFO, TOKEN
from lucifer.modules.disable import DisableAbleCommandHandler, DisableAbleRegexHandler
from lucifer.modules.helper_funcs.extraction import extract_user
from lucifer.modules.helper_funcs.filters import CustomFilters
import lucifer.modules.sql.users_sql as sql

@run_async
def info(update, context):
    args = context.args
    msg = update.effective_message  # type: Optional[Message]
    user_id = extract_user(update.effective_message, args)
    chat = update.effective_chat

    if user_id:
        user = context.bot.get_chat(user_id)

    elif not msg.reply_to_message and not args:
        user = msg.from_user

    elif not msg.reply_to_message and (not args or (
            len(args) >= 1 and not args[0].startswith("@") and not args[0].isdigit() and not msg.parse_entities(
        [MessageEntity.TEXT_MENTION]))):
        msg.reply_text("I can't extract a user from this.")
        return

    else:
        return

    del_msg = msg.reply_text("Life is <b>Short</b> Death is <b>Sure</b>...!", parse_mode=ParseMode.HTML)

    text = "<b>Knights of Hell</b>:" \
           "\n\nID: <code>{}</code>" \
           "\nFirst Name: {}".format(user.id, html.escape(user.first_name))

    if user.last_name:
        text += "\nLast Name: {}".format(html.escape(user.last_name))

    if user.username:
        text += "\nUsername: @{}".format(html.escape(user.username))

    text += "\nPermanent user link: {}".format(mention_html(user.id, "link"))

    text += "\nNumber of profile pics: {}".format(context.bot.get_user_profile_photos(user.id).total_count)
    
    knight_of_hell = False

    try:
        sw = sw.get_ban(int(user.id))
        if sw:
           text +='\n\n<b>This person is banned in Spamwatch!</b>'
           text += f'\nResason: <pre>{sw_reason}</pre>'
        else:
           pass
    except:
        pass # Don't break on exceptions like if api is down?

    if user.id == OWNER_ID:
        text += "\n\nAyy this Guy is my <b>Angel</b>!"
        knight_of_hell = True
    elif user.id in DEV_USERS:
        text += "\n\nThis person is a <b>Vampire</b>!"
        knight_of_hell = True
    elif user.id in SUDO_USERS:
        text += "\n\nThis person is a <b>Dragon</b>!"
        knight_of_hell = True
    elif user.id in SUPPORT_USERS:
        text += "\n\nThis person is a <b>Ghoul</b>!"
        knight_of_hell = True
    elif user.id in WHITELIST_USERS:
        text += "\n\nThis person is a <b>Ghost</b>!"
        knight_of_hell = True
        
    if knight_of_hell:
        text += ' [<a href="http://t.me/{}?start=knights">?</a>]'.format(context.bot.username)
        
    try:
        memstatus = chat.get_member(user.id).status
        if memstatus == 'administrator' or memstatus == 'creator':
            result = context.bot.get_chat_member(chat.id, user.id)
            if result.custom_title:
                text += f"\n\nThis user has custom title <b>{result.custom_title}</b> in this chat."
    except BadRequest:
        pass

    for mod in USER_INFO:
        try:
            mod_info = mod.__user_info__(user.id).strip()
        except TypeError:
            mod_info = mod.__user_info__(user.id, chat.id).strip()
        if mod_info:
            text += "\n\n" + mod_info

    try:
        profile = context.bot.get_user_profile_photos(user.id).photos[0][-1]
        context.bot.sendChatAction(chat.id, "upload_photo")
        context.bot.send_photo(chat.id, photo=profile, caption=(text), parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    except IndexError:
        context.bot.sendChatAction(chat.id, "typing")
        msg.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    finally:
        del_msg.delete()


INFO_HANDLER = DisableAbleCommandHandler(["info", "whois"], info, pass_args=True)
dispatcher.add_handler(INFO_HANDLER)    
