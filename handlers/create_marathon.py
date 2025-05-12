from telegram import Update
from telegram.ext import CallbackContext
from telegram.error import BadRequest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from db.marathon_queries import save_marathon
from db.member_queries import get_member_by_tg_id
from utils.is_admin import is_admin
from datetime import datetime
from utils.send_marathon_announcement import send_marathon_announcement
from telegram.ext import (
  Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
)

ASK_GROUP, ASK_NAME, ASK_DATE, ASK_DAYS, ASK_PENALTY, CONFIRM = range(6)

def start_create_marathon(update: Update, context: CallbackContext):
  user_id = update.effective_user.id

  if not is_admin(user_id):
    update.message.reply_text(
      "Упс, ничего не выйдет :) Обратись к @v_vikisa за подробностями."
    )
    return ConversationHandler.END

  update.message.reply_text(
    "Создаем марафон\\! Ты можешь отменить создание на любом этапе командой /cancel\\.\n\n"
    "🔗 Пришли ID группы, где запускаем марафон\\.\n"
    "Чтобы его узнать, напиши команду `\\/get\\_chat\\_id` в этой группе\\.",
    parse_mode="MarkdownV2"
  )

  return ASK_GROUP

def handle_group(update: Update, context: CallbackContext):
  group_ref = update.message.text

  try:
    chat = context.bot.get_chat(group_ref)
    context.user_data['group_id'] = chat.id
    context.user_data['group_title'] = chat.title
    update.message.reply_text(f"📍 Группа найдена: {chat.title}\nТеперь напиши, как будет называться марафон")
    return ASK_NAME
  except BadRequest:
    update.message.reply_text("❌ Не удалось найти группу. Убедись, что бот добавлен в группу и указана верная ссылка")
    return ASK_GROUP

def handle_name(update: Update, context: CallbackContext):
  context.user_data['marathon_name'] = update.message.text

  today = datetime.today().strftime("%d.%m.%Y")
  update.message.reply_text(
    f"📅 Укажи дату старта в формате дд\\.мм\\.гггг\n"
    f"Например: `{today}`",
    parse_mode="MarkdownV2"
  )
  return ASK_DATE

def handle_date(update: Update, context: CallbackContext):
  context.user_data['start_date'] = update.message.text  # можно парсить дату позже
  update.message.reply_text("⌛️ Сколько дней будет длиться марафон?")
  return ASK_DAYS

def handle_days(update: Update, context: CallbackContext):
  try:
    days = int(update.message.text)
    context.user_data['days'] = days
  except ValueError:
    update.message.reply_text("❗️ Количество дней должно быть числом")
    return ASK_DAYS

  update.message.reply_text("💸 Укажи стоимость пропущенного дня (в рублях):")
  return ASK_PENALTY

def handle_confirmation(update: Update, context: CallbackContext):
  query = update.callback_query
  query.answer()

  if query.data == "confirm_marathon":
    try:
      member = get_member_by_tg_id(query.from_user.id)
      if not member:
        query.edit_message_text("🚫 Что-то пошло не так")
        return ConversationHandler.END

      marathon_id = save_marathon(
        name=context.user_data['marathon_name'],
        chat_id=context.user_data['group_id'],
        start_date=context.user_data['start_date'],
        duration_days=context.user_data['days'],
        penalty=context.user_data['penalty'],
        created_by=member['id']
      )
      query.edit_message_text("✅ Марафон создан и сохранён")

      send_marathon_announcement(
        bot=context.bot,
        chat_id=context.user_data['group_id'],
        marathon_id=marathon_id,  # нужно вернуть его из save_marathon()
        name=context.user_data['marathon_name'],
        days=context.user_data['days']
      )
    except Exception as e:
      print(f"[Ошибка сохранения марафона] {e}")
      query.edit_message_text("🚫 Что-то пошло не так")
  else:
    query.edit_message_text("🚫 Создание марафона отменено.")

  return ConversationHandler.END


def ask_start_date(update: Update, context: CallbackContext):
  today = datetime.today().strftime("%d.%m.%Y")
  update.message.reply_text(
    f"📅 Укажи дату старта в формате `дд\\.мм\\.гггг`\n"
    f"Например: `{today}`",
    parse_mode="MarkdownV2"
  )
  return ASK_DATE

def handle_penalty(update: Update, context: CallbackContext):
  text = update.message.text

  try:
    penalty = int(text)
    context.user_data['penalty'] = penalty
  except ValueError:
    update.message.reply_text("❗️ Стоимость пропущенного дня должна быть числом")
    return ASK_PENALTY

  group_title = context.user_data['group_title']
  name = context.user_data['marathon_name']
  start_date = context.user_data['start_date']
  duration = context.user_data['days']
  penalty = context.user_data['penalty']

  summary = (
    f"📍 Группа: {group_title}\n"
    f"🏷 Название: {name}\n"
    f"📅 Дата старта: {start_date}\n"
    f"📆 Длительность: {duration} дней\n"
    f"💸 Штраф за пропуск дня: {penalty}₽\n\n"
    f"Подтверждаем создание марафона?"
  )

  keyboard = [
    [
      InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_marathon"),
      InlineKeyboardButton("❌ Отмена", callback_data="cancel_marathon")
    ]
  ]

  update.message.reply_text(summary, reply_markup=InlineKeyboardMarkup(keyboard))
  return CONFIRM


def cancel(update, context):
  update.message.reply_text("🚫 Окей, отменили.")
  return ConversationHandler.END
