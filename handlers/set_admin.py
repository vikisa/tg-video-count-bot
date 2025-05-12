from telegram import Update
from telegram.ext import CallbackContext
from db.member_queries import set_admin_by_username
from utils.consts import ADMIN_TG_ID

def set_admin_command(update: Update, context: CallbackContext):
  if update.effective_user.id != ADMIN_TG_ID:
    return update.message.reply_text("⛔ Только владелец может назначать админов.")

  if not context.args or not context.args[0].startswith("@"):
    return update.message.reply_text("Использование: /set_admin @username")

  username = context.args[0][1:]  # убираем @

  success = set_admin_by_username(username)
  if success:
    update.message.reply_text(f"✅ Пользователь @{username} теперь админ.")
  else:
    update.message.reply_text(f"❌ Пользователь @{username} не найден.")
