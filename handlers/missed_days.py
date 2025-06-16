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

  try:
    members = get_all_members_of_marathon(marathon_id)
    start_date = marathon["start_date"]
    end_date = marathon["end_date"]

    missing_days = get_days_with_missing_submissions(
      marathon_id, start_date, end_date, len(members)
    )

    if not missing_days:
      update.message.reply_text("✅ Нет дней с пропусками — все молодцы!")
      return

    distribution = build_day_distribution(marathon, members, missing_days)
    payments_by_user = calculate_total_payments(distribution, members)
    text = format_full_missed_report(marathon, distribution, payments_by_user, members)

    update.message.reply_text(text.strip(), parse_mode="HTML")

  except Exception as e:
    update.message.reply_text(f"⚠️ Ошибка при сборе статистики: {e}")

def calculate_total_payments(distribution_list: list, members: list):
  payments_by_user = {m["tg_id"]: 0 for m in members}
  for day in distribution_list:
    for m in members:
      if m["tg_id"] not in day["missed_tg_ids"]:
        payments_by_user[m["tg_id"]] += day["per_person_payment"]
  return payments_by_user

def build_day_distribution(marathon, members, missing_days):
  total_members = len(members)
  price = marathon["price"]
  marathon_id = marathon["id"]

  distribution = []
  for day in sorted(missing_days):
    missed_members = get_missed_members_for_day(marathon_id, day, members)
    missed_ids = [m["id"] for m in members if f"@{m['username']}" in missed_members or (not m['username'] and f"ID {m['tg_id']}" in missed_members)]
    missed_tg_ids = [m["tg_id"] for m in members if m["id"] in missed_ids]

    sent_count = total_members - len(missed_tg_ids)
    missed_count = len(missed_tg_ids)
    total_due = missed_count * price
    per_person_payment = round(total_due / sent_count, 2) if sent_count else 0

    distribution.append({
      "date": day,
      "missed_tg_ids": missed_tg_ids,
      "missed_lines": missed_members,
      "missed_count": missed_count,
      "sent_count": sent_count,
      "total_due": total_due,
      "per_person_payment": per_person_payment
    })
  return distribution

def format_full_missed_report(marathon, distribution, payments_by_user, members):
  lines = [f"<b>❌ Подробная статистика по дням с пропусками</b> ({marathon['name']}):\n"]

  for day in distribution:
    date_str = day["date"].strftime('%d.%m.%Y')
    missed_lines = "\n".join(f"• {m}" for m in day["missed_lines"]) or "—"

    lines.append(
      f"<b>{date_str}</b>\n"
      f"❌ Пропустили: {day['missed_count']} чел.\n"
      f"{missed_lines}\n"
      f"✅ Сдали: {day['sent_count']} чел.\n"
      f"💰 Долг дня: {day['total_due']}₽\n"
      f"💸 На каждого: {day['per_person_payment']}₽\n"
    )

  lines.append("<b>💸 Сводка по выплатам участников</b>\n")
  for m in sorted(members, key=lambda x: -payments_by_user[x["tg_id"]]):
    username = f"@{m['username']}" if m["username"] else f"ID {m['tg_id']}"
    amount = round(payments_by_user[m["tg_id"]], 2)
    lines.append(f"{username}: {amount}₽")

  return "\n".join(lines)

