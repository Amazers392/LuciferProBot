import html
import json
import html
import os
from typing import List, Optional

from telegram import Bot, Update, ParseMode, TelegramError
from telegram.ext import CommandHandler, run_async
from telegram.utils.helpers import mention_html

from lucifer import dispatcher, WHITELIST_USERS, SUPPORT_USERS, SUDO_USERS, DEV_USERS, OWNER_ID
from lucifer.modules.helper_funcs.chat_status import whitelist_plus, dev_plus
from lucifer.modules.helper_funcs.extraction import extract_user
from lucifer.modules.log_channel import gloggable

DEVIL_FAMILY_LIST = os.path.join(os.getcwd(), 'lucifer/devil_family.json')


def check_user_id(user_id: int, update, context) -> Optional[str]:
    if not user_id:
        reply = "That...is a chat!"

    elif user_id == context.bot.id:
        reply = "This does not work that way."

    else:
        reply = None
    return reply

@run_async
@dev_plus
@gloggable
def addsudo(update, context) -> str:
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = context.bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, update, context)
    if reply:
        message.reply_text(reply)
        return ""

    with open(DEVIL_FAMILY_LIST, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("This member is already a Sudo User")
        return ""

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Support User, Promoting to Sudo User."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        rt += "This user is already a Whitelisted User, Promoting to Sudo User."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data['sudos'].append(user_id)
    SUDO_USERS.append(user_id)

    with open(DEVIL_FAMILY_LIST, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + "\nSuccessfully added this user {} to Sudo User!".format(user_member.first_name))

    log_message = (f"#SUDO\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def addsupport(update, context) -> str:
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = context.bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, update, context)
    if reply:
        message.reply_text(reply)
        return ""

    with open(DEVIL_FAMILY_LIST, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "Demoting status of this Sudo User to Support User."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        message.reply_text("This user is already a Support User.")
        return ""

    if user_id in WHITELIST_USERS:
        rt += "Promoting Disaster level from Whitelist User to Support User."
        data['whitelists'].remove(user_id)
        WHITELIST_USERS.remove(user_id)

    data['supports'].append(user_id)
    SUPPORT_USERS.append(user_id)

    with open(DEVIL_FAMILY_LIST, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(rt + f"\n{user_member.first_name} was added as a Support User!")

    log_message = (f"#SUPPORT\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def addwhitelist(update, context) -> str:
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = context.bot.getChat(user_id)
    rt = ""

    reply = check_user_id(user_id, update, context)
    if reply:
        message.reply_text(reply)
        return ""

    with open(DEVIL_FAMILY_LIST, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        rt += "This member is a Sudo User, Demoting to Whitelist User."
        data['sudos'].remove(user_id)
        SUDO_USERS.remove(user_id)

    if user_id in SUPPORT_USERS:
        rt += "This user is already a Support User, Demoting to Whitelist User."
        data['supports'].remove(user_id)
        SUPPORT_USERS.remove(user_id)

    if user_id in WHITELIST_USERS:
        message.reply_text("This user is already a Whitelisted User.")
        return ""

    data['whitelists'].append(user_id)
    WHITELIST_USERS.append(user_id)

    with open(DEVIL_FAMILY_LIST, 'w') as outfile:
        json.dump(data, outfile, indent=4)

    update.effective_message.reply_text(
        rt + f"\nSuccessfully promoted {user_member.first_name} to a Whitelisted User!")

    log_message = (f"#WHITELIST\n"
                   f"<b>Admin:</b> {mention_html(user.id, user.first_name)} \n"
                   f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

    if chat.type != 'private':
        log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

    return log_message


@run_async
@dev_plus
@gloggable
def removesudo(update, context) -> str:
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = context.bot.getChat(user_id)

    reply = check_user_id(user_id, update, context)
    if reply:
        message.reply_text(reply)
        return ""

    with open(DEVIL_FAMILY_LIST, 'r') as infile:
        data = json.load(infile)

    if user_id in SUDO_USERS:
        message.reply_text("Demoting to normal user")
        SUDO_USERS.remove(user_id)
        data['sudos'].remove(user_id)

        with open(DEVIL_FAMILY_LIST, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNSUDO\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = "<b>{}:</b>\n".format(html.escape(chat.title)) + log_message

        return log_message

    else:
        message.reply_text("This user is not a Sudo!")
        return ""


@run_async
@dev_plus
@gloggable
def removesupport(update, context) -> str:
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = context.bot.getChat(user_id)

    reply = check_user_id(user_id, update, context)
    if reply:
        message.reply_text(reply)
        return ""

    with open(DEVIL_FAMILY_LIST, 'r') as infile:
        data = json.load(infile)

    if user_id in SUPPORT_USERS:
        message.reply_text("Demoting to Civilian")
        SUPPORT_USERS.remove(user_id)
        data['supports'].remove(user_id)

        with open(DEVIL_FAMILY_LIST, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNSUPPORT\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message

    else:
        message.reply_text("This user is not a Support User!")
        return ""


@run_async
@dev_plus
@gloggable
def removewhitelist(update, context) -> str:
    bot = context.bot
    args = context.args
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    user_id = extract_user(message, args)
    user_member = context.bot.getChat(user_id)

    reply = check_user_id(user_id, update, context)
    if reply:
        message.reply_text(reply)
        return ""

    with open(DEVIL_FAMILY_LIST, 'r') as infile:
        data = json.load(infile)

    if user_id in WHITELIST_USERS:
        message.reply_text("Demoting to normal user")
        WHITELIST_USERS.remove(user_id)
        data['whitelists'].remove(user_id)

        with open(DEVIL_FAMILY_LIST, 'w') as outfile:
            json.dump(data, outfile, indent=4)

        log_message = (f"#UNWHITELIST\n"
                       f"<b>Admin:</b> {mention_html(user.id, user.first_name)}\n"
                       f"<b>User:</b> {mention_html(user_member.id, user_member.first_name)}")

        if chat.type != 'private':
            log_message = f"<b>{html.escape(chat.title)}:</b>\n" + log_message

        return log_message
    else:
        message.reply_text("This user is not a Whitelisted User!")
        return ""


@run_async
@dev_plus
def whitelistlist(update, context):
    reply = "<b>Whitelisted Users :</b>\n"
    for each_user in WHITELIST_USERS:
        user_id = int(each_user)
        try:
            user = context.bot.get_chat(user_id)

            reply += f"• {mention_html(user_id, user.first_name)}\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@dev_plus
def supportlist(update, context):
    reply = "<b>Support Users :</b>\n"
    for each_user in SUPPORT_USERS:
        user_id = int(each_user)
        try:
            user = context.bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)} (<code>{user_id}</code>)\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@dev_plus
def sudolist(update, context):
    true_sudo = list(set(SUDO_USERS) - set(DEV_USERS))
    reply = "<b>Sudo Users :</b>\n"
    for each_user in true_sudo:
        user_id = int(each_user)
        try:
            user = context.bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)} (<code>{user_id}</code>)\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
@dev_plus
def devlist(update, context):
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply = "<b>Developers:</b>\n"
    for each_user in true_dev:
        user_id = int(each_user)
        try:
            user = context.bot.get_chat(user_id)
            reply += f"• {mention_html(user_id, user.first_name)} (<code>{user_id}</code>)\n"
        except TelegramError:
            pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)

@run_async
@dev_plus
def botstaff(update, context):
    try:
        ownerbot = int(OWNER_ID)
        ownerid = context.bot.get_chat(ownerbot)
        reply = f"<b>Owner:</b> {mention_html(ownerbot, ownerid.first_name)} (<code>{ownerbot}</code>)\n"
    except TelegramError:
        pass
    true_dev = list(set(DEV_USERS) - {OWNER_ID})
    reply += "\n<b>Developers:</b>\n"
    if true_dev == []:
        reply += "No Dev Users"
    else:
        for each_user in true_dev:
            user_id = int(each_user)
            try:
                user = context.bot.get_chat(user_id)
                reply += f"• {mention_html(user_id, user.first_name)} (<code>{user_id}</code>)\n"
            except TelegramError:
                pass
    true_sudo = list(set(SUDO_USERS) - set(DEV_USERS))
    reply += "\n<b>Sudo Users:</b>\n"
    if true_sudo == []:
        reply += "No Sudo Users"
    else:
        for each_user in true_sudo:
            user_id = int(each_user)
            try:
                user = context.bot.get_chat(user_id)
                reply += f"• {mention_html(user_id, user.first_name)} (<code>{user_id}</code>)\n"
            except TelegramError:
                pass
    reply += "\n<b>Support Users:</b>\n"
    if SUPPORT_USERS == []:
        reply += "No Support Users"
    else:
        for each_user in SUPPORT_USERS:
            user_id = int(each_user)
            try:
                user = context.bot.get_chat(user_id)
                reply += f"• {mention_html(user_id, user.first_name)} (<code>{user_id}</code>)\n"
            except TelegramError:
                pass
    reply += "\n<b>Whitelisted Users:</b>\n"
    if WHITELIST_USERS == []:
        reply += "No additional whitelisted users"
    else:
        for each_user in WHITELIST_USERS:
            user_id = int(each_user)
            try:
                user = context.bot.get_chat(user_id)

                reply += f"• {mention_html(user_id, user.first_name)} (<code>{user_id}</code>)\n"
            except TelegramError:
                pass
    update.effective_message.reply_text(reply, parse_mode=ParseMode.HTML)


SUDO_HANDLER = CommandHandler("addsudo", addsudo, pass_args=True)
SUPPORT_HANDLER = CommandHandler("addsupport", addsupport, pass_args=True)
WHITELIST_HANDLER = CommandHandler("addwhitelist", addwhitelist, pass_args=True)
UNSUDO_HANDLER = CommandHandler("rmsudo", removesudo, pass_args=True)
UNSUPPORT_HANDLER = CommandHandler("rmsupport", removesupport, pass_args=True)
UNWHITELIST_HANDLER = CommandHandler("rmwhitelist", removewhitelist, pass_args=True)

WHITELISTLIST_HANDLER = CommandHandler("whitelists", whitelistlist)
SUPPORTLIST_HANDLER = CommandHandler("supports", supportlist)
SUDOLIST_HANDLER = CommandHandler("sudos", sudolist)
DEVLIST_HANDLER = CommandHandler("devs", devlist)
BOTSTAFF_HANDLER = CommandHandler("botstaff", botstaff)

dispatcher.add_handler(SUDO_HANDLER)
dispatcher.add_handler(SUPPORT_HANDLER)
dispatcher.add_handler(WHITELIST_HANDLER)
dispatcher.add_handler(UNSUDO_HANDLER)
dispatcher.add_handler(UNSUPPORT_HANDLER)
dispatcher.add_handler(UNWHITELIST_HANDLER)

dispatcher.add_handler(WHITELISTLIST_HANDLER)
dispatcher.add_handler(SUPPORTLIST_HANDLER)
dispatcher.add_handler(SUDOLIST_HANDLER)
dispatcher.add_handler(DEVLIST_HANDLER)
dispatcher.add_handler(BOTSTAFF_HANDLER)

__mod_name__ = "Bot Staff"
__handlers__ = [SUDO_HANDLER, SUPPORT_HANDLER, WHITELIST_HANDLER,
                UNSUDO_HANDLER, UNSUPPORT_HANDLER, UNWHITELIST_HANDLER,
                WHITELISTLIST_HANDLER, SUPPORTLIST_HANDLER, SUDOLIST_HANDLER, DEVLIST_HANDLER, BOTSTAFF_HANDLER]
