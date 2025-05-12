from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from db.marathon_queries import get_active_marathon_by_chat
from db.member_queries import get_member_by_tg_id
from utils.consts import ADMIN_TG_ID

def show_active_marathon_command(update: Update, context: CallbackContext):
  chat = update.effective_chat
  user = update.effective_user

  if chat.type not in ["group", "supergroup"]:
    update.message.reply_text("⛔ Эту команду нужно вызывать из группы")
    return

  member = get_member_by_tg_id(user.id)
  if not member or not member["is_admin"]:
    if user.id != ADMIN_TG_ID:
      update.message.reply_text("⛔ Только админ группы может вызывать эту команду")
      return

  marathon = get_active_marathon_by_chat(chat.id)

  if not marathon:
    update.message.reply_text("Нет активных марафонов для этой группы.")
    return

  try:
    keyboard = InlineKeyboardMarkup([
      [
        InlineKeyboardButton("✅ Участвую", callback_data=f"join:{marathon['id']}"),
        InlineKeyboardButton("❌ Пас", callback_data=f"pass:{marathon['id']}")
      ]
    ])

    text = (
      f"Повторно публикуем активный марафон:\n\n"
      f"🏷 Название: *{marathon['name']}*\n"
      f"📅 Срок: {marathon['start_date'].strftime('%d.%m.%Y')} – {marathon['end_date'].strftime('%d.%m.%Y')}\n\n"
      f"Подтверди участие!"
    )

    update.message.reply_text(text, reply_markup=keyboard, parse_mode="Markdown")

  except Exception as e:
    # Отправка тебе в личку
    context.bot.send_message(
      chat_id=248146008,  # твой Telegram ID
      text=f"❌ Ошибка при /show_active_marathon в чате {chat.id}: {e}"
    )
