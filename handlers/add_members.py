from telegram import Update, User
from telegram.ext import CallbackContext
from db.queries import get_or_create_member, get_marathon_id_and_start, add_member_to_marathon

def add_members_command(update: Update, context: CallbackContext):
  if len(context.args) < 2:
    update.effective_message.reply_text('Формат: /add_marathon_members <марафон> @user1 @user2 ...')
    return

  marathon_name = context.args[0]
  mentions = update.effective_message.entities[1:]  # пропускаем /command

  marathon = get_marathon_id_and_start(marathon_name)
  if not marathon:
    update.effective_message.reply_text('Марафон не найден')
    return

  marathon_id, start_date = marathon
  added = []

  for entity in mentions:
    if entity.type not in ("mention", "text_mention"):
      continue

    user = update.effective_message.parse_entities().get(entity)

    if not isinstance(user, User):
      continue

    tg_id = user.id
    username = user.username or "без_ника"
    member_id = get_or_create_member(tg_id, username)
    add_member_to_marathon(member_id, marathon_id, start_date)
    added.append("@" + username)

  update.effective_message.reply_text(f"Добавлены в марафон {marathon_name}: {', '.join(added)}")
