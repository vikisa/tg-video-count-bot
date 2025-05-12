from telegram import Update, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils.is_admin import is_admin

YOUR_TG_ID = 248146008

def remove_buttons_command(update: Update, context: CallbackContext):
  user_id = update.effective_user.id
  if user_id != YOUR_TG_ID or not is_admin(user_id):
    update.message.reply_text("⛔ Только админ может удалять кнопки вручную")
    return

  if not update.message.reply_to_message:
    update.message.reply_text("ℹ️ Ответь этой командой на сообщение с кнопками")
    return

  try:
    replied = update.message.reply_to_message
    chat_id = replied.chat.id
    message_id = replied.message_id

    context.bot.edit_message_reply_markup(
      chat_id=chat_id,
      message_id=message_id,
      reply_markup=None
    )

  except Exception as e:
    return
