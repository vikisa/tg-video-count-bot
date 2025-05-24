from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime, date
from db.member_queries import get_member_id_by_username
from db.queries import add_illness, is_admin
from utils.errors import reply_error
from utils.get_moscow_today import get_moscow_today_date

def add_ill_command(update: Update, context: CallbackContext):
  if len(context.args) != 3:
    update.effective_message.reply_text('Формат: /add_ill @username <дата> <дней>')
    return

  raw_username, raw_date, raw_count = context.args
  username = raw_username.lstrip('@')

  try:
    start_date = datetime.strptime(raw_date, "%d-%m-%Y").date()
    day_count = int(raw_count)

    sender_id = update.effective_user.id
    admin = is_admin(sender_id)

    if start_date < get_moscow_today_date() and not admin:
      update.effective_message.reply_text("Нельзя добавлять болезнь задним числом")
      return
  except Exception as e:
    reply_error(update, "Ошибка", e)
    return

  user_id = get_member_id_by_username(username)
  if not user_id:
    update.effective_message.reply_text("Участник не найден в системе")
    return

  add_illness(user_id, start_date, day_count)
  update.effective_message.reply_text(f"🛌 @{username} отдыхает с {start_date} на {day_count} дней")
