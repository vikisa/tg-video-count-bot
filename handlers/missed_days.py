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
    print('distribution', distribution)
    payments_by_user = calculate_total_payments(distribution, members)
    print('payments_by_user',payments_by_user)
    text = format_full_missed_report(marathon, distribution, payments_by_user, members)

    update.message.reply_text(text.strip(), parse_mode="HTML")

  except Exception as e:
    update.message.reply_text(f"⚠️ Ошибка при сборе статистики: {e}")

def calculate_total_payments(distribution, members):
  payments_by_user = {m["tg_id"]: 0 for m in members}

  for day in distribution:
    missed_set = set(day["missed_tg_ids"])  # для быстрого поиска
    for m in members:
      tg_id = m["tg_id"]
      if tg_id not in missed_set:
        payments_by_user[tg_id] += day["per_person_payment"]

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
  lines = [f"<b>Расчёт по призам</b> ({marathon['name']}):\n"]

  for day in distribution:
    date_str = day["date"].strftime('%d.%m.%Y')
    missed_lines = "\n".join(f"• {m}" for m in day["missed_lines"]) or "—"

    lines.append(
      f"<b>{date_str}</b>\n"
      f"❌ Пропустили: {day['missed_count']}\n"
      f"{missed_lines}\n"
      f"✅ Сдали: {day['sent_count']}\n"
      f"💰 Общая сумма за день: {day['total_due']}₽\n"
      f"💸 Выплата участнице за день: {day['per_person_payment']}₽\n"
    )

  lines.append("<b>💸 Сводка по призам:</b>\n")
  for m in sorted(members, key=lambda x: -payments_by_user[x["tg_id"]]):
    username = f"@{m['username']}" if m["username"] else f"ID {m['tg_id']}"
    amount = round(payments_by_user[m["tg_id"]], 2)
    lines.append(f"{username}: {amount}₽")

  return "\n".join(lines)

