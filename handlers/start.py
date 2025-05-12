from telegram import Update
from telegram.ext import CallbackContext
from db.member_queries import create_member
from utils.consts import ADMIN_TG_ID

def start_command(update: Update, context: CallbackContext):
  user = update.effective_user
  chat_type = update.effective_chat.type

  if chat_type == "private":
    tg_id = user.id
    username = user.username or ""

    create_member(tg_id, username)

    update.message.reply_text(
      f"Привет! 👋 Я бот для проведения марафонов\n"
      "Чтобы начать, используй команду /create_marathon"
    )

    context.bot.send_message(
      chat_id=ADMIN_TG_ID,
      text=(
        f"👤 Новый пользователь:\n"
        f"👾 username: @{user.username or 'без ника'}\n"
        f"🆔 telegram_id: {user.id}\n"
      )
    )
  elif chat_type in ["group", "supergroup"]:
    update.message.reply_text("Я работаю! Используй /help, чтобы узнать, что я умею")
