from telegram import Update
from telegram.ext import CallbackContext
from db.marathon_queries import get_active_marathon_by_chat
from db.marathon_members import get_participant_usernames
from db.member_queries import get_member_by_tg_id

YOUR_TG_ID = 248146008

def show_participants_command(update: Update, context: CallbackContext):
  chat = update.effective_chat
  user = update.effective_user

  member = get_member_by_tg_id(user.id)
  if not (member and member["is_admin"]) and user.id != YOUR_TG_ID:
    update.message.reply_text("⛔ Только админ может запрашивать список участниц.")
    return

  marathon = get_active_marathon_by_chat(chat.id)
  if not marathon:
    update.message.reply_text("❌ Активный марафон не найден.")
    return

  try:
    participants = get_participant_usernames(marathon["id"])
    if not participants:
      text = f"📢 Марафон <b>«{marathon['name']}»</b> пока без участниц."
    else:
      names = "\n".join(f"• @{u}" for u in participants)
      text = (
        f"✅ Участницы:\n{names}"
      )

    context.bot.send_message(
      chat_id=chat.id,
      text=text,
      parse_mode="HTML"
    )

  except Exception as e:
    context.bot.send_message(YOUR_TG_ID, f"⚠️ Ошибка при выводе участников: {e}")
