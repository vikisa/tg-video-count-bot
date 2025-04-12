from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime
from utils.errors import reply_error
from db.queries import insert_marathon

def create_marathon_command(update: Update, context: CallbackContext):
  if len(context.args) != 4:
    update.effective_message.reply_text('Формат: /create_marathon <название> <начало в формате дд.мм.гггг> <конец дд.мм.гггг> <стоимость прогула>')
    return

  name, start_str, end_str, price_str = context.args

  try:
    start_date = datetime.strptime(start_str, '%d.%m.%Y').date()
    end_date = datetime.strptime(end_str, '%d.%m.%Y').date()
    price = int(price_str)
  except ValueError as e:
    reply_error(update, "Неверный формат", e)

  try:
    insert_marathon(name, start_date, end_date, price)
    update.effective_message.reply_text(f"✅ Марафон '{name}' создан!")
  except Exception as e:
    reply_error(update, 'Неверный формат', e)
