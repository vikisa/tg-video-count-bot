from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime, date
from db.queries import get_member_id_by_username, add_illness, is_admin
from utils.errors import reply_error

def add_ill_command(update: Update, context: CallbackContext):
  if len(context.args) != 3:
    update.message.reply_text('Формат: /add-ill @username <дата> <дней>')
    return

  raw_username, raw_date, raw_count = context.args
  username = raw_username.lstrip('@')

  try:
    start_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
    day_count = int(raw_count)

    sender_id = update.effective_user.id
    admin = is_admin(sender_id)

    if start_date < date.today() and not admin:
      update.message.reply_text("Нельзя добавлять болезнь задним числом")
      return
  except Exception as e:
    reply_error(update, "Ошибка", e)
    return

  user_id = get_member_id_by_username(username)
  if not user_id:
    update.message.reply_text("Участник не найден в системе")
    return

  add_illness(user_id, start_date, day_count)
  update.message.reply_text(f"🛌 @{username} отдыхает с {start_date} на {day_count} дней")
