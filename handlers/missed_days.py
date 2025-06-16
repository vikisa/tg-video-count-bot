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
    day_distributions = []

    for day in sorted(missing_days):

      # Кто не сдал
      missed_members = get_missed_members_for_day(marathon_id, day, members)
      missed_ids = [m["id"] for m in members if f"@{m['username']}" in missed_members or (not m['username'] and f"ID {m['tg_id']}" in missed_members)]
      missed_tg_ids = [m["tg_id"] for m in members if m["id"] in missed_ids]
      missed_tg = missed_members

      # Кто сдал
      sent_count = total_members - len(missed_tg)
      missed_count = len(missed_tg)

      total_due = missed_count * price
      per_person_payment = round(total_due / sent_count, 2) if sent_count > 0 else 0

      date_str = day.strftime('%d.%m.%Y')
      missed_formatted = "\n".join(f"• {m}" for m in missed_tg)

      day_distributions.append({
        "date": day,
        "missed_tg_ids": missed_tg_ids,
        "per_person_payment": per_person_payment
      })

      full_text += (
        f"<b>{date_str}</b>\n"
        f"❌ Пропустили: {missed_count}\n"
        f"{missed_formatted if missed_formatted else '—'}\n"
        f"✅ Сдали: {sent_count}\n"
        f"💰 Общая сумма за день: {total_due}₽\n"
        f"💸 Выплата за день: {per_person_payment}₽\n\n"
      )

    payments_by_user = {m["tg_id"]: 0 for m in members}

    for day in day_distributions:
      for m in members:
        tg_id = m["tg_id"]
        if tg_id not in day["missed_tg_ids"]:
          payments_by_user[tg_id] += day["per_person_payment"]

    # Вывод по каждому участнику
    full_text += "<b>💸 Сводка по выплатам участников</b>\n\n"
    for m in sorted(members, key=lambda x: -payments_by_user[x["tg_id"]]):
      tg_id = m["tg_id"]
      username = f"@{m['username']}" if m["username"] else f"ID {tg_id}"
      amount = round(payments_by_user[tg_id], 2)
      full_text += f"{username}: {amount}₽\n"

    update.message.reply_text(full_text.strip(), parse_mode="HTML")

  except Exception as e:
    update.message.reply_text(f"⚠️ Ошибка при сборе статистики: {e}")

def calculate_total_payments(distribution_list: list, members: list) -> list:
  # tg_id → сумма выплат
  payments_by_user = {m["tg_id"]: 0 for m in members}

  for day in distribution_list:
    for m in members:
      tg_id = m["tg_id"]
      if tg_id not in day["missed_tg_ids"]:
        payments_by_user[tg_id] += day["per_person_payment"]

  # Округляем до копеек
  return [
    {
      "tg_id": tg_id,
      "username": next((m["username"] for m in members if m["tg_id"] == tg_id), None),
      "total": round(amount, 2)
    }
    for tg_id, amount in payments_by_user.items()
  ]

def format_user_payments(user_payments: list) -> str:
  lines = ["<b>💰 Суммарные выплаты по участникам</b>\n"]
  for u in sorted(user_payments, key=lambda x: -x["total"]):
    name = f"@{u['username']}" if u["username"] else f"ID {u['tg_id']}"
    lines.append(f"{name}: {u['total']}₽")
  return "\n".join(lines)
