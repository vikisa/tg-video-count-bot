from typing import TypedDict
from telegram.ext import CallbackContext
from telegram import Update

class ReplyDict(TypedDict):
  update: Update
  context: CallbackContext