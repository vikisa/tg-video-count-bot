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
  price = marathon["price"]

  try:
    missing_days = get_days_with_missing_submissions(marathon_id, start_date, end_date, total_members)

    if not missing_days:
      update.message.reply_text("✅ Нет дней с пропусками — все молодцы!")
      return

    full_text = f"<b>❌ Подробная статистика по дням с пропусками</b> ({marathon['name']}):\n\n"

    for day in sorted(missing_days):

      # Кто не сдал
      missed_members = get_missed_members_for_day(marathon_id, day, members)
      missed_ids = [m["id"] for m in members if f"@{m['username']}" in missed_members or (not m['username'] and f"ID {m['tg_id']}" in missed_members)]
      missed_tg = missed_members

      # Кто сдал
      sent_count = total_members - len(missed_tg)
      missed_count = len(missed_tg)

      total_due = missed_count * price
      per_person_payment = round(total_due / sent_count, 2) if sent_count > 0 else 0

      date_str = day.strftime('%d.%m.%Y')
      missed_formatted = "\n".join(f"• {m}" for m in missed_tg)

      full_text += (
        f"<b>{date_str}</b>\n"
        f"❌ Пропустили: {missed_count}\n"
        f"{missed_formatted if missed_formatted else '—'}\n"
        f"✅ Сдали: {sent_count}\n"
        f"💰 Общая сумма за день: {total_due}₽\n"
        f"💸 Выплата за день: {per_person_payment}₽\n\n"
      )

    update.message.reply_text(full_text.strip(), parse_mode="HTML")

  except Exception as e:
    update.message.reply_text(f"⚠️ Ошибка при сборе статистики: {e}")