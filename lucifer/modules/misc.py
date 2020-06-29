import html
import random, re
import wikipedia
from typing import Optional, List
from requests import get

from io import BytesIO
from random import randint
import requests as r

from telegram import (Message,
Chat, MessageEntity,
InlineKeyboardMarkup,
InlineKeyboardButton,
ParseMode, ChatAction,
TelegramError)

from telegram.ext import CommandHandler, run_async, Filters
from telegram.utils.helpers import escape_markdown, mention_html
from telegram.error import BadRequest

from lucifer import dispatcher, OWNER_ID, SUDO_USERS, DEV_USERS, SUPPORT_USERS, WHITELIST_USERS, WALL_API, sw
from lucifer.__main__ import STATS, USER_INFO, GDPR
from lucifer.modules.disable import DisableAbleCommandHandler
from lucifer.modules.helper_funcs.extraction import extract_user
from lucifer.modules.helper_funcs.filters import CustomFilters
from lucifer.modules.helper_funcs.alternate import send_action
from lucifer.modules.helper_funcs.chat_status import dev_plus


@run_async
def get_id(update, context):
    args = context.args
    user_id = extract_user(update.effective_message, args)
    if user_id:
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.forward_from:
            user1 = update.effective_message.reply_to_message.from_user
            user2 = update.effective_message.reply_to_message.forward_from
            update.effective_message.reply_text(
                "The original sender, {}, has an ID of `{}`.\nThe forwarder, {}, has an ID of `{}`.".format(
                    escape_markdown(user2.first_name),
                    user2.id,
                    escape_markdown(user1.first_name),
                    user1.id),
                parse_mode=ParseMode.MARKDOWN)
        else:
            user = context.bot.get_chat(user_id)
            update.effective_message.reply_text("{}'s id is `{}`.".format(escape_markdown(user.first_name), user.id),
                                                parse_mode=ParseMode.MARKDOWN)
    else:
        chat = update.effective_chat  # type: Optional[Chat]
        if chat.type == "private":
            update.effective_message.reply_text("Your id is `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

        else:
            update.effective_message.reply_text("This group's id is `{}`.".format(chat.id),
                                                parse_mode=ParseMode.MARKDOWN)

@run_async
def gdpr(update, context):
    update.effective_message.reply_text("Deleting identifiable data...")
    for mod in GDPR:
        mod.__gdpr__(update.effective_user.id)

    update.effective_message.reply_text("Your personal data has been deleted.\n\nNote that this will not unban "
                                        "you from any chats, as that is telegram data, not Skylee data. "
                                        "Flooding, warns, and gbans are also preserved, as of "
                                        "[this](https://ico.org.uk/for-organisations/guide-to-the-general-data-protection-regulation-gdpr/individual-rights/right-to-erasure/), "
                                        "which clearly states that the right to erasure does not apply "
                                        "\"for the performance of a task carried out in the public interest\", as is "
                                        "the case for the aforementioned pieces of data.",
                                        parse_mode=ParseMode.MARKDOWN)


MARKDOWN_HELP = """
Markdown is a very powerful formatting tool supported by telegram. {} has some enhancements, to make sure that \
saved messages are correctly parsed, and to allow you to create buttons.
- <code>_italic_</code>: wrapping text with '_' will produce italic text
- <code>*bold*</code>: wrapping text with '*' will produce bold text
- <code>`code`</code>: wrapping text with '`' will produce monospaced text, also known as 'code'
- <code>[sometext](someURL)</code>: this will create a link - the message will just show <code>sometext</code>, \
and tapping on it will open the page at <code>someURL</code>.
EG: <code>[test](example.com)</code>
- <code>[buttontext](buttonurl:someURL)</code>: this is a special enhancement to allow users to have telegram \
buttons in their markdown. <code>buttontext</code> will be what is displayed on the button, and <code>someurl</code> \
will be the url which is opened.
EG: <code>[This is a button](buttonurl:example.com)</code>
If you want multiple buttons on the same line, use :same, as such:
<code>[one](buttonurl://example.com)
[two](buttonurl://google.com:same)</code>
This will create two buttons on a single line, instead of one button per line.
Keep in mind that your message <b>MUST</b> contain some text other than just a button!
""".format(dispatcher.bot.first_name)


@run_async
def markdown_help(update, context):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text("Try forwarding the following message to me, and you'll see!")
    update.effective_message.reply_text("/save test This is a markdown test. _italics_, *bold*, `code`, "
                                        "[URL](example.com) [button](buttonurl:github.com) "
                                        "[button2](buttonurl://google.com:same)")

@run_async
def wiki(update, context):
    kueri = re.split(pattern="wiki", string=update.effective_message.text)
    wikipedia.set_lang("en")
    if len(str(kueri[1])) == 0:
        update.effective_message.reply_text("Enter keywords!")
    else:
        try:
            pertama = update.effective_message.reply_text("🔄 Loading...")
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="🔧 More Info...", url=wikipedia.page(kueri).url)]])
            context.bot.editMessageText(chat_id=update.effective_chat.id, message_id=pertama.message_id, text=wikipedia.summary(kueri, sentences=10), reply_markup=keyboard)
        except wikipedia.PageError as e:
            update.effective_message.reply_text(f"⚠ Error: {e}")
        except BadRequest as et :
            update.effective_message.reply_text(f"⚠ Error: {et}")
        except wikipedia.exceptions.DisambiguationError as eet:
            update.effective_message.reply_text(f"⚠ Error\n There are too many query! Express it more!\nPossible query result:\n{eet}")

@run_async
def ud(update, context):
    msg = update.effective_message
    args = context.args
    text = " ".join(args).lower()
    if not text:
       msg.reply_text("Please enter keywords to search!")
       return
    elif text == 'starry':
       msg.reply_text("Fek off bitch!")
       return
    try:
        results = get(f'http://api.urbandictionary.com/v0/define?term={text}').json()
        reply_text = f'Word: {text}\nDefinition: {results["list"][0]["definition"]}'
        reply_text += f'\n\nExample: {results["list"][0]["example"]}'
    except IndexError:
        reply_text = f'Word: {text}\nResults: Sorry could not find any matching results!'
    ignore_chars = "[]"
    reply = reply_text
    for chars in ignore_chars:
        reply = reply.replace(chars, "")
    return msg.reply_text(reply)
    

@run_async
@send_action(ChatAction.UPLOAD_PHOTO)
def wall(update, context):
    chat_id = update.effective_chat.id
    msg = update.effective_message
    msg_id = update.effective_message.message_id
    args = context.args
    query = " ".join(args)
    if not query:
        msg.reply_text("Please enter a query!")
        return
    else:
        caption = query
        term = query.replace(" ", "%20")
        json_rep = r.get(f"https://wall.alphacoders.com/api2.0/get.php?auth={WALL_API}&method=search&term={term}").json()
        if not json_rep.get("success"):
            msg.reply_text("An error occurred!")

        else:
            wallpapers = json_rep.get("wallpapers")
            if not wallpapers:
                msg.reply_text("No results found! Refine your search.")
                return
            else:
                index = randint(0, len(wallpapers)-1) # Choose random index
                wallpaper = wallpapers[index]
                wallpaper = wallpaper.get("url_image")
                wallpaper = wallpaper.replace("\\", "")
                context.bot.send_photo(chat_id, photo=wallpaper, caption='Preview',
                reply_to_message_id=msg_id, timeout=60)
                context.bot.send_document(chat_id, document=wallpaper,
                filename='wallpaper', caption=caption, reply_to_message_id=msg_id,
                timeout=60)
                

@run_async
@send_action(ChatAction.UPLOAD_PHOTO)
def rmemes(update, context):
    msg = update.effective_message
    chat = update.effective_chat

    SUBREDS = ['meirl', 'dankmemes', 'AdviceAnimals',
               'memes', 'meme', 'memes_of_the_dank',
               'PornhubComments', 'teenagers', 'memesIRL',
               'insanepeoplefacebook', 'terriblefacebookmemes']

    subreddit = random.choice(SUBREDS)
    res = r.get(
          f"https://meme-api.herokuapp.com/gimme/{subreddit}")

    if res.status_code != 200: # Like if api is down?
       msg.reply_text('Sorry some error occurred :(')
       return
    else:
       res = res.json()

    rpage = res.get(str('subreddit')) # Subreddit
    title = res.get(str('title')) # Post title
    memeu = res.get(str('url')) # meme pic url
    plink = res.get(str('postLink'))

    caps = f"× <b>Title</b>: {title}\n"
    caps += f"× <b>Subreddit:</b> <pre>r/{rpage}</pre>"

    keyb = [[InlineKeyboardButton(
           text="Subreddit Postlink 🔗", url=plink)]]
    try:
       context.bot.send_photo(chat.id, photo=memeu,
                   caption=(caps),
                   reply_markup=InlineKeyboardMarkup(keyb),
                   timeout=60,
                   parse_mode=ParseMode.HTML)

    except BadRequest as excp:
           return msg.reply_text(f"Error! {excp.message}")


@run_async
@dev_plus
def stats(update, context):
    update.effective_message.reply_text("Current stats:\n" + "\n".join([mod.__stats__() for mod in STATS]))
    


# /ip is for private use
__help__ = """
An "odds and ends" module for small, simple commands which don't really fit anywhere
 • /info: Get information about a user.
 • /wiki : Search wikipedia articles.
 • /rmeme: Sends random meme scraped from reddit.
 • /ud <query> : Search stuffs in urban dictionary.
 • /wall <query> : Get random wallpapers directly from bot! 
 • /reverse : Reverse searches image or stickers on google.
 • /gdpr: Deletes your information from the bot's database. Private chats only.
 • /markdownhelp: Quick summary of how markdown works in telegram - can only be called in private chats.
"""

__mod_name__ = "Miscs"

ID_HANDLER = DisableAbleCommandHandler("id", get_id, pass_args=True)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, filters=Filters.private)
GDPR_HANDLER = CommandHandler("gdpr", gdpr, filters=Filters.private)
WIKI_HANDLER = DisableAbleCommandHandler("wiki", wiki)
WALLPAPER_HANDLER = DisableAbleCommandHandler("wall", wall, pass_args=True)
UD_HANDLER = DisableAbleCommandHandler("ud", ud)
REDDIT_MEMES_HANDLER = DisableAbleCommandHandler("rmeme", rmemes)
STATS_HANDLER = CommandHandler("stats", stats)

dispatcher.add_handler(WALLPAPER_HANDLER)
dispatcher.add_handler(UD_HANDLER)
dispatcher.add_handler(ID_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)
dispatcher.add_handler(GDPR_HANDLER)
dispatcher.add_handler(WIKI_HANDLER)
dispatcher.add_handler(REDDIT_MEMES_HANDLER)
dispatcher.add_handler(STATS_HANDLER)
