from telegram import Update
from telegram.ext import CallbackContext
from datetime import datetime
from db.queries import (
  get_marathon_participants,
  get_members_who_submitted,
  get_members_ill_that_day,
  get_marathon_id_by_name
)

def day_stat_command(update: Update, context: CallbackContext):
  if len(context.args) < 2:
    update.effective_message.reply_text("Формат: /day_stat <марафон> <дата>")
    return

  name = context.args[0]
  try:
    target_date = datetime.strptime(context.args[1], "%Y-%m-%d").date()
  except:
    update.effective_message.reply_text("Неверный формат даты")
    return

  marathon_id = get_marathon_id_by_name(name)
  if not marathon_id:
    update.effective_message.reply_text("Марафон не найден")
    return

  participants = get_marathon_participants(marathon_id)
  submitted = get_members_who_submitted(marathon_id, target_date)
  ill = get_members_ill_that_day(target_date)

  present = []
  missing = []

  for member_id, name in participants:
    if member_id in ill:
      continue
    elif member_id in submitted:
      present.append(name)
    else:
      missing.append(name)

  text = f"""📅 Статистика за {target_date}:
✅ Сдали: {', '.join(present) or 'никто'}
❌ Не сдали: {', '.join(missing) or 'никого'}"""
  update.effective_message.reply_text(text)
