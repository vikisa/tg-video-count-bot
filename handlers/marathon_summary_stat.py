from db.marathon_members import get_all_members_of_marathon
from db.payments_queries import get_total_payments_by_member
from db.day_results import count_missed_days_for_member
from db.marathon_queries import get_active_marathon_by_chat
from telegram import Bot
CHAT_ID = int(-1002579802998)
from telegram import Update
from telegram.ext import CallbackContext
from utils.consts import ADMIN_TG_ID

def get_marathon_summary_stat(marathon_id: int) -> str:
  marathon = get_active_marathon_by_chat(CHAT_ID)
  if not marathon:
    return "❌ Марафон не найден."

  start_date = marathon["start_date"]
  end_date = marathon["end_date"]
  price = marathon["price"]

  total_days = (end_date - start_date).days + 1
  print('total days', total_days)
  members = get_all_members_of_marathon(marathon_id)

  lines = []

  for member in members:
    member_id = member["id"]
    username = f"@{member['username']}" if member["username"] else f"ID {member['tg_id']}"

    missed_days = count_missed_days_for_member(marathon_id, member_id, total_days)
    due = missed_days * price

    paid = get_total_payments_by_member(marathon_id, member_id)

    lines.append(f"{username} {due}₽ / {paid}₽")

  if not lines:
    return "❌ Нет участников в марафоне."

  return "<b>📊 Сводка по марафону</b>\n\n" + "\n".join(lines)

def summary_command(update: Update, context: CallbackContext):
  user = update.effective_user
  chat_type = update.effective_chat.type

  if chat_type != "private" or user.id != ADMIN_TG_ID:
    update.message.reply_text("Ничего не выйдет")
    return

  if len(context.args) != 1:
    update.message.reply_text("❌ Использование: /summary <marathon_id>")
    return

  try:
    marathon_id = int(context.args[0])
  except ValueError:
    update.message.reply_text("❌ ID марафона должен быть числом.")
    return

  try:
    text = get_marathon_summary_stat(marathon_id)
    update.message.reply_text(text, parse_mode="HTML")
  except Exception as e:
    update.message.reply_text(f"⚠️ Ошибка при сборе статистики: {e}")