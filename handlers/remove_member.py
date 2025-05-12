from telegram import Update
from telegram.ext import CallbackContext
from db.member_queries import remove_member
from utils.consts import ADMIN_TG_ID

def remove_member_command(update: Update, context: CallbackContext):
  user = update.effective_user
  chat_type = update.effective_chat.type

  if chat_type == "private":
    try:
      tg_id = user.id

      remove_member(tg_id)

      context.bot.send_message(
        chat_id=ADMIN_TG_ID,
        text=(
          f"👤 Новый пользователь:\n"
          f"👾 username: @{user.username or 'без ника'}\n"
          f"🆔 telegram_id: {user.id}\n"
        )
      )

    except Exception as e:
      update.message.reply_text("Участник удален")