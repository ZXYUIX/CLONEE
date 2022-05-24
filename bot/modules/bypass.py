import time

from telegram.ext import CommandHandler
from bot import LOGGER, dispatcher
from bot.helper.ext_utils.bot_utils import *
from bot.helper.ext_utils.bypass_parser import *
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage, deleteMessage
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters


@new_thread
def bypassNode(update, context):
    LOGGER.info('User: {} [{}]'.format(update.message.from_user.first_name, update.message.from_user.id))
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    link = ''
    if len(args) > 1:
        link = args[1]
    if reply_to is not None:
        if len(link) == 0:
            link = reply_to.text
    is_gplinks = is_gplinks_link(link)
    is_adfly = is_adfly_link(link)
    is_rocklinks = is_rocklinks_link(link)
    is_droplink = is_droplink_link(link)
    if (is_gplinks or is_adfly or is_rocklinks or is_droplink):
      msg = sendMessage(f"<b>✨✨ Bypassing ✨✨:</b> <code>{link}</code>", context.bot, update)
      LOGGER.info(f"Bypassing: {link}")
      if is_gplinks:
        link = gplinks_bypass(link)
      if is_adfly:
        link = adfly_bypass(link)
      if is_rocklinks:
        link = rocklinks_bypass(link)
      if is_droplink:
        link = droplink_bypass(link)
        
      deleteMessage(context.bot, msg)
      msg = sendMessage(f"<b>✨✨ Bypassed Link ✨✨:</b> <code>{link}</code>", context.bot, update)
      LOGGER.info(f"✨✨ Bypassed Link ✨✨: {link}")
      
      
bypass_handler = CommandHandler(BotCommands.BypassCommand, bypassNode,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(bypass_handler)
