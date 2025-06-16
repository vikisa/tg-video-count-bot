import os
from dotenv import load_dotenv
from telegram.ext import (
  Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
)

from handlers.add_payment import add_payment_command
from handlers.start import start_command
from handlers.get_chat_id import get_chat_id_command
from handlers.create_marathon import (
  start_create_marathon, handle_group, handle_name,
  handle_date, handle_days, handle_confirmation, cancel, handle_penalty,
  ASK_GROUP, ASK_NAME, ASK_DATE, ASK_DAYS, ASK_PENALTY, CONFIRM
)
from handlers.show_active_marathon import show_active_marathon_command
from handlers.handle_participation_callback import handle_participation_callback
from handlers.set_admin import set_admin_command
from handlers.show_participants import show_participants_command
from handlers.help import help_command
from handlers.remove_buttons import remove_buttons_command
from handlers.handle_video import handle_video
from handlers.day_stat import day_stat_command
from handlers.remove_member import remove_member_command
from handlers.add_marathon_member import add_marathon_member_command
from handlers.scheduler import start_scheduler
from handlers.marathon_summary_stat import summary_command
from handlers.missed_days import missed_days_command

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

def main():
  updater = Updater(token=TOKEN, use_context=True)
  dp = updater.dispatcher

  dp.add_handler(CommandHandler('help', help_command))
  dp.add_handler(CommandHandler('start', start_command))

  # команды в личном чате
  # пошаговое создание марафона
  conv_handler = ConversationHandler(
    entry_points=[CommandHandler('create_marathon', start_create_marathon)],
    states={
      ASK_GROUP: [MessageHandler(Filters.text & ~Filters.command, handle_group)],
      ASK_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_name)],
      ASK_DATE: [MessageHandler(Filters.text & ~Filters.command, handle_date)],
      ASK_DAYS: [MessageHandler(Filters.text & ~Filters.command, handle_days)],
      ASK_PENALTY: [MessageHandler(Filters.text & ~Filters.command, handle_penalty)],
      CONFIRM: [CallbackQueryHandler(handle_confirmation)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
  )
  dp.add_handler(conv_handler)
  dp.add_handler(CommandHandler('set_admin', set_admin_command))
  dp.add_handler(CommandHandler('remove_member', remove_member_command))
  dp.add_handler(CommandHandler('add_marathon_member', add_marathon_member_command))
  dp.add_handler(CommandHandler('add_payment', add_payment_command))
  dp.add_handler(CommandHandler("summary", summary_command))
  dp.add_handler(CommandHandler('missed_days', missed_days_command))

  # команды в группе
  dp.add_handler(CommandHandler('get_chat_id', get_chat_id_command))
  dp.add_handler(CommandHandler('show_active_marathon', show_active_marathon_command))
  dp.add_handler(CommandHandler('remove_buttons', remove_buttons_command))
  dp.add_handler(CommandHandler('show_participants', show_participants_command))
  dp.add_handler(CallbackQueryHandler(handle_participation_callback, pattern=r"^(join|pass):\d+$"))
  dp.add_handler(CommandHandler('day_stat', day_stat_command))

  # приём видео
  dp.add_handler(MessageHandler(Filters.video & Filters.chat_type.groups, handle_video))

  start_scheduler()

  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()