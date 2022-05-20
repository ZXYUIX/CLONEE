import os
import requests
from magic import Magic
from bot.helper.ext_utils.bot_utils import *
from bot.helper.telegram_helper.message_utils import sendMessage, deleteMessage
from bot.helper.telegram_helper.bot_commands import BotCommands
from logging import getLogger, ERROR, DEBUG
from time import time
from pickle import load as pload
from json import loads as jsnloads
from os import makedirs, path as ospath, listdir, 
from requests.utils import quote as rquote
from io import FileIO
from re import search as re_search
from urllib.parse import parse_qs, urlparse
from random import randrange
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from telegram import InlineKeyboardMarkup
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type, before_log, RetryError
from bot import parent_id, DOWNLOAD_DIR, IS_TEAM_DRIVE, DRIVE_INDEX_URL, USE_SERVICE_ACCOUNTS

LOGGER = getLogger(__name__)
getLogger('googleapiclient.discovery').setLevel(ERROR)

if USE_SERVICE_ACCOUNTS:
    SERVICE_ACCOUNT_INDEX = randrange(len(listdir("accounts")))
    
def get_mime_type(file_path):
    mime = Magic(mime=True)
    mime_type = mime.from_file(file_path)
    mime_type = mime_type or "text/plain"
    return mime_type
    
class GoogleDriveHelper:

    def __init__(self, name=None, listener=None):
      self.listener = listener
        self.name = name
        self.__G_DRIVE_TOKEN_FILE = "token.json"
        # Check https://developers.google.com/drive/scopes for all available scopes
        self.__OAUTH_SCOPE = ['https://www.googleapis.com/auth/drive']
        self.__G_DRIVE_DIR_MIME_TYPE = "application/vnd.google-apps.folder"
        self.__G_DRIVE_BASE_DOWNLOAD_URL = "https://drive.google.com/uc?id={}&export=download"
        self.__G_DRIVE_DIR_BASE_DOWNLOAD_URL = "https://drive.google.com/drive/folders/{}"
        self.__service = self.authorize()
        self.batch_dict = {}
        self.telegraph_content = []
        self.path = []
        self.total_bytes = 0
        self.total_files = 0
        self.total_folders = 0
        self.transferred_size = 0
        self.alt_auth = False
      
      
@new_thread
def mirrorNode(update, context):
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
      msg = sendMessage(f"<b>Can't mirror GDrive Links!! Use /clone for mirroring GDrive Links!!</b>", context.bot, update)
      LOGGER.info(f"Can't mirror GDrive Links!! Use /clone for mirroring GDrive Links!!")
      return msg
    else:
      try:
        msg = sendMessage(f"<b>Mirroring:</b> <code>{link}</code>", context.bot, update)
        LOGGER.info(f"Mirroring: {link}")
        result = mirror(link)
        filename = link.split("/")[-1]
        loc = DOWNLOAD_DIR+filename
        filesize = ospath.getsize(loc)
        msg += f'<b>Filename: </b><code>{file.get("name")}</code>'
        buttons = ButtonMaker()
        buttons.buildbutton("☁️ Drive Link", result)
        if INDEX_URL is not None:
          iresult = f'{INDEX_URL}/{filename}'
          buttons.buildbutton("☁️ Drive Link", iresult)
      
      except Exception as err:
        msg = f"Error"
        return msg, ""
  return msg, InlineKeyboardMarkup(buttons.build_menu(2))
             
        
def mirror(link):
  r = requests.get(link, stream = True)
  # No Dependency
  filename = link.split("/")[-1]
  loc = DOWNLOAD_DIR+filename
  with open(loc, "wb") as file:
  # Always write format like (.txt/.mp3/.mp4/.pdf/.json/.iso)
	  for block in r.iter_content(chunk_size = 1024):
		  if block:
			  file.write(block)
  mimefile = get_mime_type(loc)
  file_metadata = {
            'name': filename,
            'description': 'Uploaded by SearchX-bot',
            'mimeType': mimefile,
        }
  if ospath.getsize(loc) == 0:
            media_body = MediaFileUpload(loc,
                                         mimetype=mimefile,
                                         resumable=False)
            response = self.__service.files().create(supportsAllDrives=True,
                                                              body=file_metadata, media_body=media_body).execute()
          
  media_body = MediaFileUpload(loc,
                               mimetype=mimefile,
                               resumable=True,
                               chunksize=50 * 1024 * 1024)
  drive_file = self.__service.files().create(supportsAllDrives=True,
                                                   body=file_metadata, media_body=media_body)
  response = None
  drive_file = self.__service.files().get(supportsAllDrives=True, fileId=response['id']).execute()
  download_url = self.__G_DRIVE_BASE_DOWNLOAD_URL.format(drive_file.get('id'))
  return download_url

mirror_handler = CommandHandler(BotCommands.CloneCommand, mirrorNode,
                               filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
dispatcher.add_handler(mirror_handler)
