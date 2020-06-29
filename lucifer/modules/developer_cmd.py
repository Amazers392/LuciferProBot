from io import BytesIO
from time import sleep
from typing import Optional, List
from telegram import TelegramError, Chat, Message
from telegram import Update, Bot
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, CommandHandler
from telegram.ext.dispatcher import run_async
from lucifer.modules.helper_funcs.chat_status import is_user_ban_protected, dev_plus

import lucifer.modules.sql.users_sql as sql
from lucifer.modules.sql.users_sql import get_all_users
from lucifer import dispatcher, OWNER_ID, LOGGER, SUDO_USERS, SUPPORT_USERS, DEV_USERS, WHITELIST_USERS
from lucifer.modules.helper_funcs.filters import CustomFilters

USERS_GROUP = 4
CHAT_GROUP = 10


@run_async
@dev_plus
def quickscope(update, context):
    args = context.args
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        context.bot.kick_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted banning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
@dev_plus
def quickunban(update, context):
    args = context.args
    if args:
        chat_id = str(args[1])
        to_kick = str(args[0])
    else:
        update.effective_message.reply_text("You don't seem to be referring to a chat/user")
    try:
        context.bot.unban_chat_member(chat_id, to_kick)
        update.effective_message.reply_text("Attempted unbanning " + to_kick + " from" + chat_id)
    except BadRequest as excp:
        update.effective_message.reply_text(excp.message + " " + to_kick)


@run_async
@dev_plus
def banall(update, context):
    args = context.args
    if args:
        chat_id = str(args[0])
        all_mems = sql.get_chat_members(chat_id)
    else:
        chat_id = str(update.effective_chat.id)
        all_mems = sql.get_chat_members(chat_id)
    for mems in all_mems:
        try:
            context.bot.kick_chat_member(chat_id, mems.user)
            update.effective_message.reply_text("Tried banning " + str(mems.user))
            sleep(0.1)
        except BadRequest as excp:
            update.effective_message.reply_text(excp.message + " " + str(mems.user))
            continue


@run_async
@dev_plus
def snipe(update, context):
    args = context.args
    try:
        chat_id = str(args[0])
        del args[0]
    except TypeError as excp:
        update.effective_message.reply_text("Please give me a chat to echo to!")
    to_send = " ".join(args)
    if len(to_send) >= 2:
        try:
            context.bot.sendMessage(int(chat_id), str(to_send))
        except TelegramError:
            LOGGER.warning("Couldn't send to group %s", str(chat_id))
            update.effective_message.reply_text("Couldn't send the message. Perhaps I'm not part of that group?")
            
   
@run_async
@dev_plus
def leave(update, context):

    args = context.args
    
    if args:
        chat_id = str(args[0])
        try:
            context.bot.leave_chat(int(chat_id))
            update.effective_message.reply_text("I left that chat!.")
        except TelegramError:
            update.effective_message.reply_text("I could not leave that group")
    else:
        update.effective_message.reply_text("Send a valid chat ID") 


@run_async
@dev_plus
def staffids(update, context):
    sfile = 'List of Botstaffs:\n'
    sfile += f'× DEV USER IDs; {DEV_USERS}\n'
    sfile += f'× SUDO USER IDs; {SUDO_USERS}\n'
    sfile += f'× SUPPORT USER IDs; {SUPPORT_USERS}\n'
    sfile += f'× WHITELIST USER IDs; {WHITELIST_USERS}'
    with BytesIO(str.encode(sfile)) as output:
         output.name = "botstaffs.txt"
         update.effective_message.reply_document(
           document=output, filename="botstaffs.txt",
           caption="Here is the list of Botstaffs.")
        

@run_async
@dev_plus
def echo(update, context):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message
    if message.reply_to_message:
        message.reply_to_message.reply_text(args[1])
    else:
        message.reply_text(args[1], quote=False)
    message.delete()


@run_async
@dev_plus
def getlink(update, context):
    args = context.args
    message = update.effective_message
    if args:
        pattern = re.compile(r'-\d+')
    else:
        message.reply_text("You don't seem to be referring to any chats.")
    links = "Invite link(s):\n"
    for chat_id in pattern.findall(message.text):
        try:
            chat = context.bot.getChat(chat_id)
            bot_member = chat.get_member(context.bot.id)
            if bot_member.can_invite_users:
                invitelink = context.bot.exportChatInviteLink(chat_id)
                links += str(chat_id) + ":\n" + invitelink + "\n"
            else:
                links += str(chat_id) + ":\nI don't have access to the invite link." + "\n"
        except BadRequest as excp:
                links += str(chat_id) + ":\n" + excp.message + "\n"
        except TelegramError as excp:
                links += str(chat_id) + ":\n" + excp.message + "\n"

    message.reply_text(links)    
    

@run_async
@dev_plus
def chats(update, context):
    all_chats = sql.get_all_chats() or []
    chatfile = 'List of chats.\n'
    for chat in all_chats:
        chatfile += "{} - ({})\n".format(chat.chat_name, chat.chat_id)

    with BytesIO(str.encode(chatfile)) as output:
        output.name = "chatlist.txt"
        update.effective_message.reply_document(document=output, filename="chatlist.txt",
                                                caption="Here is the list of chats in my database.")

@run_async
def chat_checker(update, context):
  if update.effective_message.chat.get_member(context.bot.id).can_send_messages == False:
    context.bot.leaveChat(update.effective_message.chat.id)
    
    
@run_async
@dev_plus
def broadcast(update, context):
    to_send = update.effective_message.text.split(None, 1)
    if len(to_send) >= 2:
        chats = sql.get_all_chats() or []
        failed = 0
        for chat in chats:
            try:
                context.bot.sendMessage(int(chat.chat_id), to_send[1])
                sleep(0.1)
            except TelegramError:
                failed += 1
                LOGGER.warning("Couldn't send broadcast to %s, group name %s", str(chat.chat_id), str(chat.chat_name))

        update.effective_message.reply_text("Broadcast complete. {} groups failed to receive the message, probably "
                                            "due to being kicked.".format(failed))



@run_async
@dev_plus
def msgtoall(update, context):

    to_send = update.effective_message.text.split(None, 1)

    if len(to_send) >= 2:
        users = get_all_users()
        failed_user = 0
        for user in users:
            try:
                context.bot.sendMessage(int(user.user_id), to_send[1])
                sleep(0.1)
            except TelegramError:
                failed_user += 1
                LOGGER.warning("Couldn't send broadcast to %s", str(user.user_id))

        update.effective_message.reply_text(
            f"Broadcast complete. {failed_user} failed to receive message, probably due to being blocked"
            )       
        
SNIPE_HANDLER = CommandHandler("snipe", snipe, pass_args=True)
BANALL_HANDLER = CommandHandler("banall", banall, pass_args=True)
QUICKSCOPE_HANDLER = CommandHandler("quickscope", quickscope, pass_args=True)
QUICKUNBAN_HANDLER = CommandHandler("quickunban", quickunban, pass_args=True)
LEAVE_HANDLER = CommandHandler("leave", leave, pass_args = True)
STAFFIDS_HANDLER = CommandHandler("staffids", staffids)
ECHO_HANDLER = CommandHandler("echo", echo)
GETLINK_HANDLER = CommandHandler("getlink", getlink, pass_args=True)
BROADCAST_HANDLER = CommandHandler("broadcast", broadcast)
MSGTOALL_HANDLER = CommandHandler("msgtoall", msgtoall)
CHATLIST_HANDLER = CommandHandler("chatlist", chats)
CHAT_CHECKER_HANDLER = MessageHandler(Filters.all & Filters.group, chat_checker)

dispatcher.add_handler(SNIPE_HANDLER)
dispatcher.add_handler(BANALL_HANDLER)
dispatcher.add_handler(QUICKSCOPE_HANDLER)
dispatcher.add_handler(QUICKUNBAN_HANDLER)
dispatcher.add_handler(LEAVE_HANDLER)
dispatcher.add_handler(GETLINK_HANDLER)
dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(STAFFIDS_HANDLER)
dispatcher.add_handler(BROADCAST_HANDLER)
dispatcher.add_handler(MSGTOALL_HANDLER)
dispatcher.add_handler(CHATLIST_HANDLER)
dispatcher.add_handler(CHAT_CHECKER_HANDLER, CHAT_GROUP)
