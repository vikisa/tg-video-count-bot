from db.day_results import get_days_with_missing_submissions, get_missed_members_for_day
from db.marathon_members import get_all_members_of_marathon
from db.marathon_queries import get_active_marathon_by_chat
CHAT_ID = int(-1002579802998)
from telegram import Update
from telegram.ext import CallbackContext
from utils.consts import ADMIN_TG_ID

def missed_days_command(update: Update, context: CallbackContext):
  user = update.effective_user
  chat_type = update.effective_chat.type

  if chat_type != "private" or user.id != ADMIN_TG_ID:
    update.message.reply_text("Ничего не выйдет")
    return

  try:
    marathon_id = int(context.args[0])
  except ValueError:
    update.message.reply_text("❌ ID марафона должен быть числом.")
    return

  marathon = get_active_marathon_by_chat(CHAT_ID)
  if not marathon:
    update.message.reply_text("❌ Марафон не найден.")
    return

  members = get_all_members_of_marathon(marathon_id)
  total_members = len(members)
  start_date = marathon["start_date"]
  end_date = marathon["end_date"]

  try:
    missing_days = get_days_with_missing_submissions(marathon_id, start_date, end_date, total_members)

    if not missing_days:
      update.message.reply_text("✅ Нет дней с пропусками — все молодцы!")
      return

    full_text = f"<b>❌ Пропуски по дням</b> ({marathon['name']}):\n\n"

    for day in sorted(missing_days):
      missed_users = get_missed_members_for_day(marathon_id, day, members)
      day_str = day.strftime('%d.%m.%Y')
      if missed_users:
        users_text = "\n".join(f"• {u}" for u in missed_users)
        full_text += f"<b>{day_str}</b>\n{users_text}\n\n"
      else:
        full_text += f"<b>{day_str}</b>\n(все сдали?)\n\n"

    update.message.reply_text(full_text.strip(), parse_mode="HTML")

  except Exception as e:
    update.message.reply_text(f"⚠️ Ошибка при сборе статистики: {e}")