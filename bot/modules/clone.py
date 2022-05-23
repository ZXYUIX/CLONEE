import time

from telegram.ext import CommandHandler

from bot import LOGGER, dispatcher
from bot.helper.drive_utils.gdriveTools import GoogleDriveHelper
from bot.helper.ext_utils.bot_utils import *
from bot.helper.ext_utils.clone_status import CloneStatus
from bot.helper.ext_utils.exceptions import DDLException
from bot.helper.ext_utils.parser import unified, gdtot, udrive
from bot.helper.telegram_helper.message_utils import sendMessage, editMessage, deleteMessage
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.filters import CustomFilters

@new_thread
def cloneNode(update, context):
    LOGGER.info('User: {} [{}]'.format(update.message.from_user.first_name, update.message.from_user.id))
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    link = ''
    if len(args) > 1:
        link = args[1]
    if reply_to is not None:
        if len(link) == 0:
            link = reply_to.text
    is_appdrive = is_appdrive_link(link)
    is_gdtot = is_gdtot_link(link)
    is_gdflix = is_gdflix_link(link)
    is_driveapp = is_driveapp_link(link)
    is_drivelinks = is_drivelinks_link(link)
    is_drivebit = is_drivebit_link(link)
    is_drivesharer = is_drivesharer_link(link)
    is_hubdrive = is_hubdrive_link(link)
    is_katdrive = is_katdrive_link(link)
    is_kolop = is_kolop_link(link)
    is_drivefire = is_drivefire_link(link)
    if (is_gdtot  or is_gdflix or is_driveapp or is_drivelinks or is_drivebit or is_drivesharer or is_hubdrive or is_katdrive or is_kolop or is_drivefire):
        try:
            msg = sendMessage(f"<b>Processing:</b> <code>{link}</code>", context.bot, update)
            LOGGER.info(f"Processing: {link}")
            if is_appdrive:
                link = appdrive(link)
            if is_gdtot:
                link = gdtot(link)
            if is_gdflix:
                link = unified(link)
            if is_driveapp:
                link = unified(link)
            if is_drivelinks:
                link = unified(link)
            if is_drivebit:
                link = unified(link)
            if is_drivesharer:
                link = unified(link)
            if is_hubdrive:
                link = udrive(link)
            if is_katdrive:
                link = udrive(link)
            if is_kolop:
                link = udrive(link)
            if is_drivefire:
                link = udrive(link)
            deleteMessage(context.bot, msg)
        except DDLException as e:
            deleteMessage(context.bot, msg)
            LOGGER.error(e)
            return sendMessage(str(e), context.bot, update)
    if is_gdrive_link(link):
        msg = sendMessage(f"<b>Cloning:</b> <code>{link}</code>", context.bot, update)
        LOGGER.info(f"Cloning: {link}")
        status_class = CloneStatus()
        gd = GoogleDriveHelper()
        sendCloneStatus(link, msg, status_class, update, context)
        result = gd.clone(link, status_class)
        deleteMessage(context.bot, msg)
        status_class.set_status(True)
        sendMessage(result, context.bot, update)
        if (is_appdrive or is_gdtot or is_gdflix or is_driveapp or is_drivelinks or is_drivebit or is_drivesharer or is_hubdrive or is_katdrive or is_kolop or is_drivefire):
            LOGGER.info(f"Deleting: {link}")
            gd.deleteFile(link)
    else:
        sendMessage("<b>Send a Drive / AppDrive / DriveApp / GDToT link along with command</b>", context.bot, update)
        LOGGER.info("Cloning: None")

@new_thread
def sendCloneStatus(link, msg, status, update, context):
    old_statmsg = ''
    while not status.done():
        time.sleep(3)
        try:
            statmsg = f"<b>Cloning:</b> <a href='{status.source_folder_link}'>{status.source_folder_name}</a>\n━━━━━━━━━━━━━━" \
                      f"\n<b>Current file:</b> <code>{status.get_name()}</code>\n\n<b>Transferred</b>: <code>{status.get_size()}</code>"
            if not statmsg == old_statmsg:
                editMessage(statmsg, msg)
                old_statmsg = statmsg
        except Exception as e:
            if str(e) == "Message to edit not found":
                break
            time.sleep(2)
            continue
    return

clone_handler = CommandHandler(BotCommands.CloneCommand, cloneNode,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(clone_handler)
