import os
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from handlers.create_marathon import create_marathon_command
from handlers.add_members import add_members_command
from handlers.add_ill import add_ill_command
from handlers.day_stat import day_stat_command
from handlers.handle_video import handle_video

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

def main():
  updater = Updater(token=TOKEN, use_context=True)
  dp = updater.dispatcher

  # команды
  dp.add_handler(CommandHandler("create_marathon", create_marathon_command))
  dp.add_handler(CommandHandler("add_maraphon_members", add_members_command))
  dp.add_handler(CommandHandler("add_ill", add_ill_command))
  dp.add_handler(CommandHandler("day_stat", day_stat_command))

  # приём видео
  dp.add_handler(MessageHandler(Filters.video, handle_video))

  updater.start_polling()
  updater.idle()

if __name__ == '__main__':
  main()
