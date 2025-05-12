from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.consts import ADMIN_TG_ID
from db.marathon_queries import set_marathon_message_id

def send_marathon_announcement(bot, chat_id, marathon_id, name, days):
  try:
    keyboard = InlineKeyboardMarkup([
      [
        InlineKeyboardButton("✅ Участвую", callback_data=f"join:{marathon_id}"),
        InlineKeyboardButton("❌ Пас", callback_data=f"pass:{marathon_id}")
      ]
    ])

    text = f'Создан марафон: *"{name}"*\nДлительность: {days} дней.\nПодтверди участие!'
    bot.send_message(
      chat_id=chat_id,
      text=text,
      reply_markup=keyboard,
      parse_mode='Markdown'
    )

  except Exception as e:
    bot.send_message(
      chat_id=ADMIN_TG_ID,
      text=f"❌ Ошибка при отправке сообщения в чат {chat_id}: {e}"
    )
