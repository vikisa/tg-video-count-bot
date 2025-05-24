from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from zoneinfo import ZoneInfo
from telegram import Bot
import os
from dotenv import load_dotenv
from db.marathon_members import get_all_members_of_marathon
from db.day_results import get_members_who_sent_video
from utils.get_yesterday_day import get_yesterday_date

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

bot = Bot(token=BOT_TOKEN)

def send_midnight_stat():
  selected_date = get_yesterday_date()

  all_members = get_all_members_of_marathon(-1002579802998)
  sent_ids = get_members_who_sent_video(-1002579802998, selected_date)
  all_ids = {m["id"] for m in all_members}
  missed_ids = all_ids - sent_ids

  if not missed_ids and sent_ids:
    bot.send_message(
      chat_id=CHAT_ID,
      text=f"🏆 {selected_date.strftime('%d.%m.%Y')} — все умнички!",
      parse_mode="HTML"
    )
    return

  missed = [f"• @{m['username']}" if m['username'] else f"• ID {m['tg_id']}"
            for m in all_members if m["id"] in missed_ids]

  text = (
    f"📊 Статистика за <b>{selected_date.strftime('%d.%m.%Y')}</b>\n\n"

    f"❌ Пропустили:\n" + ("\n".join(missed) if missed else "— никто")
  )

  bot.send_message(
    chat_id=CHAT_ID,
    text=text,
    parse_mode="HTML"
  )

def start_scheduler():
  scheduler = BackgroundScheduler()
  trigger = CronTrigger(hour=0, minute=0, timezone=ZoneInfo("Europe/Moscow"))
  scheduler.add_job(send_midnight_stat, trigger)
  scheduler.start()
