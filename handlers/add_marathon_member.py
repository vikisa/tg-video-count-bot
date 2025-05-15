from telegram import Update
from telegram.ext import CallbackContext
from db.member_queries import create_member
from db.marathon_members import add_participant
from datetime import datetime
from zoneinfo import ZoneInfo
from utils.consts import ADMIN_TG_ID

def add_marathon_member_command(update: Update, context: CallbackContext):
  chat = update.effective_chat
  user = update.effective_user

  if chat.type != 'private' or user.id != ADMIN_TG_ID:
    return update.message.reply_text(f"Ничего не выйдет:)")

  if len(context.args) != 3 or not context.args[0].startswith("@"):
    return update.message.reply_text('Использование: /add_marathon_member @username <marathon_id> <дд.мм.гггг>')

  username = context.args[0][1:]  # убираем "@"
  try:
    marathon_id = int(context.args[1])
    join_date = datetime.strptime(context.args[2], "%d.%m.%Y")
    join_datetime = join_date.replace(hour=12, tzinfo=ZoneInfo("Europe/Moscow"))
  except Exception as e:
    return update.message.reply_text(f"❌ Неверный формат данных: {e}")

  # попытка получить tg_id по username через get_chat_member
  try:
    # бот должен быть в общей группе с пользователем
    chat_id = update.effective_chat.id
    member = context.bot.get_chat_member(chat_id=chat_id, user_id=f"@{username}")
    tg_id = member.user.id
  except Exception as e:
    return update.message.reply_text(f"❌ Не удалось получить пользователя @{username}: {e}")

  try:
    create_member(tg_id, username)
    add_participant(tg_id, marathon_id, join_datetime)
    update.message.reply_text(
      f"✅ @{username} добавлен в марафон {marathon_id} с {context.args[2]} (12:00 МСК)"
    )
  except Exception as e:
    update.message.reply_text(f"❌ Ошибка при добавлении: {e}")
