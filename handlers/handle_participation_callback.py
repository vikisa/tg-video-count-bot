from db.marathon_members import add_participant, remove_participant, count_participants
from db.member_queries import get_member_by_tg_id
from utils.consts import ADMIN_TG_ID
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext

def handle_participation_callback(update: Update, context: CallbackContext):
  query = update.callback_query
  query.answer()

  data = query.data  # "join:12" или "pass:12"
  user = query.from_user
  action, marathon_id = data.split(":")
  marathon_id = int(marathon_id)

  member = get_member_by_tg_id(user.id)
  if not member:
    context.bot.send_message(chat_id=ADMIN_TG_ID, text=f"❌ Неизвестный участник: {user.id} @{user.username}")
    return

  try:
    if action == "join":
      add_participant(marathon_id, member['id'])
    elif action == "pass":
      remove_participant(marathon_id, member['id'])

    total = count_participants(marathon_id)

    new_buttons = InlineKeyboardMarkup([[
      InlineKeyboardButton(f"✅ Участвую ({total})", callback_data=f"join:{marathon_id}"),
      InlineKeyboardButton("❌ Пас", callback_data=f"pass:{marathon_id}")
    ]])

    query.edit_message_reply_markup(reply_markup=new_buttons)

  except Exception as e:
    context.bot.send_message(chat_id=ADMIN_TG_ID, text=f"⚠️ Ошибка при участии: {e}")
    query.edit_message_text("🚫 Что-то пошло не так. Попробуйте позже.")
