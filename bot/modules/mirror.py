import os
import requests

from logging import getLogger, ERROR, DEBUG
from time import time
from pickle import load as pload
from json import loads as jsnloads
from os import makedirs, path as ospath, listdir
from requests.utils import quote as rquote
from io import FileIO
from re import search as re_search
from timeit import default_timer as timer
from urllib.parse import parse_qs, urlparse
from random import randrange

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from tenacity import *

from telegram import InlineKeyboardMarkup
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_log, RetryError
from bot import parent_id, DOWNLOAD_DIR, IS_TEAM_DRIVE, DRIVE_INDEX_URL, USE_SERVICE_ACCOUNTS
from bot.helper.drive_utils.gdriveTools import *
from bot.helper.telegram_helper.button_build import ButtonMaker
from bot.helper.ext_utils.bot_utils import *
from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage, editMessage
from bot.helper.telegram_helper.bot_commands import BotCommands

      
@new_thread
def mirrorNode(update, context):
  LOGGER.info('User: {} [{}]'.format(update.message.from_user.first_name, update.message.from_user.id))
    args = update.message.text.split(" ", maxsplit=1)
    reply_to = update.message.reply_to_message
    link = ''
    gd = GoogleDriveHelper()
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
      msg = sendMessage(f"<b>Can't mirror GDrive Links!! Use /clone for mirroring GDrive Links!!</b>", context.bot, update)
      LOGGER.info(f"Can't mirror GDrive Links!! Use /clone for mirroring GDrive Links!!")
      return msg
    else:
      try:
        msg = sendMessage(f"<b>Mirroring:</b> <code>{link}</code>", context.bot, update)
        LOGGER.info(f"Mirroring: {link}")
        result = gd.mirror(link)
        filename = link.split("/")[-1]
        loc = DOWNLOAD_DIR+filename
        filesize = ospath.getsize(loc)
        msg += f'<b>Filename: </b><code>{file.get("name")}</code>'
        buttons = ButtonMaker()
        buttons.buildbutton("☁️ Drive Link", result)
        if DRIVE_INDEX_URL is not None:
          iresult = f'{DRIVE_INDEX_URL}/{filename}'
          buttons.buildbutton("☁️ Drive Link", iresult)
      
      except Exception as err:
        msg = f"Error"
        return msg, ""
  return msg, InlineKeyboardMarkup(buttons.build_menu(2))
             

mirror_handler = CommandHandler(BotCommands.CloneCommand, mirrorNode,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(mirror_handler)
