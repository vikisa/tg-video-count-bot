from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from contextlib import nullcontext
import os
from dotenv import load_dotenv
from utils.get_yesterday_day import get_yesterday_date
import pytz
from utils.day_stat import get_day_stat

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(-1002579802998)

bot = Bot(token=BOT_TOKEN)

def send_midnight_stat():
  selected_date = get_yesterday_date()

  get_day_stat(selected_date, nullcontext(), True)

def start_scheduler():
  moscow_tz = pytz.timezone("Europe/Moscow")
  scheduler = BackgroundScheduler()
  trigger = CronTrigger(hour=0, minute=0, timezone=moscow_tz)
  scheduler.add_job(send_midnight_stat, trigger)
  scheduler.start()
