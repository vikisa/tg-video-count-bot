from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime
from zoneinfo import ZoneInfo
from db.member_queries import create_member, get_member_by_tg_id
from db.marathon_members import add_participant
from utils.consts import ADMIN_TG_ID

def add_to_marathon_command(update: Update, context: CallbackContext):
  user = update.effective_user
  chat = update.effective_chat
  reply = update.message.reply_to_message

  if chat.type not in ["group", "supergroup"] or user.id != ADMIN_TG_ID:
    return update.message.reply_text("Ничего не выйдет:)")

  if not reply:
    context.bot.send_message(chat_id=ADMIN_TG_ID, text="❗ Используй команду в ответ на сообщение участника")
    return

  if len(context.args) != 2:
    context.bot.send_message(chat_id=ADMIN_TG_ID, text="Использование: /add_to_marathon <marathon_id> <дд.мм.гггг>")
    return

  try:
    marathon_id = int(context.args[0])
    join_date = datetime.strptime(context.args[1], "%d.%m.%Y")
    join_datetime = join_date.replace(hour=12, tzinfo=ZoneInfo("Europe/Moscow"))
  except Exception as e:
    context.bot.send_message(chat_id=ADMIN_TG_ID, text=f"Неверный формат даты: {e}")
    return

  target_user = reply.from_user
  tg_id = target_user.id
  username = target_user.username

  try:
    create_member(tg_id, username)
    member = get_member_by_tg_id(tg_id)
    add_participant(marathon_id, member["id"], join_datetime)

    update.message.reply_text(f"✅ ок")
  except Exception as e:
    context.bot.send_message(chat_id=ADMIN_TG_ID, text=f"❌ Ошибка при добавлении участника: {e}")
    return
