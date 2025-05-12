from telegram import Update
from telegram.ext import CallbackContext

def get_chat_id_command(update: Update, context: CallbackContext):
  chat = update.effective_chat
  user = update.effective_user

  if chat.type not in ["group", "supergroup"]:
    update.message.reply_text("⛔ Эту команду нужно запускать из группы")
    return

  chat_id = chat.id
  update.message.reply_text(
    f"🆔 ID этой группы: `{chat_id}`\n",
    parse_mode="Markdown"
  )
