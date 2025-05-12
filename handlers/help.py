from telegram import Update
from telegram.ext import CallbackContext

def help_command(update: Update, context: CallbackContext):
  chat = update.effective_chat

  if chat.type == "private":
    update.message.reply_text(
      "🧭 <b>Справка</b>\n\n"
      "💼 Управление:\n"
      "• /create_marathon — пошаговое создание марафона\n"
      "• <code>/set_admin @username</code> — назначить администратора\n\n"
      "🛠 Служебное:\n"
      "• /help — эта справка\n\n"
      "Если хочешь привязать марафон к группе:\n"
      "1. Добавь бота в группу\n"
      "2. Напиши в группе <code>/get_chat_id</code>\n"
      "3. Используй chat_id при создании марафона",
      parse_mode="HTML"
    )

  else:
    update.message.reply_text(
      "📍 *Команды, доступные в группе:*\n\n"
      "• /get_chat_id — узнать ID текущей группы\n"
      "• /show_active_marathon — повторно опубликовать кнопки участия\n"
      "• <code>/remove_buttons</code> — скрыть кнопки участия\n"
      "• /show_participants — вывести участников\n"
      "• /help — показать эту справку",
      parse_mode="HTML"
    )
