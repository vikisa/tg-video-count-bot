from telegram import Update
from telegram.ext import CallbackContext
from db.member_queries import get_member_id_by_username
from db.payments_queries import insert_payment
from utils.consts import ADMIN_TG_ID

def add_payment_command(update: Update, context: CallbackContext):
  user = update.effective_user
  chat_type = update.effective_chat.type

  if chat_type != "private" or user.id != ADMIN_TG_ID:
    update.message.reply_text("Ничего не выйдет")
    return

  if len(context.args) != 3:
    update.message.reply_text("❌ Использование: /add_payment <marathon_id> <tg_id> <amount>")
    return

  try:
    marathon_id = int(context.args[0])
    tg_id = context.args[1].replace('@', '')
    amount = int(context.args[2])
  except ValueError:
    update.message.reply_text("Что-то не так с аргументами")
    return

  member_id = get_member_id_by_username(tg_id)
  if not member_id:
    update.message.reply_text("Участник не найден")
    return

  insert_payment(marathon_id=marathon_id, member_id=member_id, payment=amount)
  update.message.reply_text(f"✅ Платёж на сумму {amount}₽ добавлен для участника {tg_id}.")
