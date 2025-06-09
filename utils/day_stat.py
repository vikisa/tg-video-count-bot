from contextlib import nullcontext
from utils.consts import ADMIN_TG_ID
from db.marathon_members import get_all_members_of_marathon
from db.marathon_queries import get_active_marathon_by_chat
from db.day_results import get_members_who_sent_video
from telegram.ext import CallbackContext
from telegram import Update
from typing import TypedDict, Union
from utils.types import ReplyDict
CHAT_ID = int(-1002579802998)
from dotenv import load_dotenv
import os
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
from telegram import Bot
bot = Bot(token=BOT_TOKEN)

def get_day_stat(date, reply: Union[ReplyDict, nullcontext], is_bot: bool):
  update: Update = reply['update']
  context: CallbackContext = reply['context']

  marathon = get_active_marathon_by_chat(CHAT_ID)

  if not marathon:
    if not is_bot:
      update.message.reply_text("❌ Активный марафон не найден.")
    else:
      bot.send_message(
        chat_id=CHAT_ID,
        text="❌ Активный марафон не найден.",
      )
    return

  if date < marathon["start_date"]:
    if not is_bot:
      update.message.reply_text(
        f"❌ Статистика за {date.strftime('%d.%m.%Y')} невозможна — марафон ещё не начался.",
        parse_mode="HTML"
      )
    else:
      bot.send_message(
        chat_id=CHAT_ID,
        text=f"❌ Статистика за {date.strftime('%d.%m.%Y')} невозможна — марафон ещё не начался.",
        parse_mode="HTML"
      )
    return

  try:
    all_members = get_all_members_of_marathon(marathon["id"])
    sent_ids = get_members_who_sent_video(marathon["id"], date)
    all_ids = {m["id"] for m in all_members}
    missed_ids = all_ids - sent_ids

    if not missed_ids and sent_ids:
      if not is_bot:
        update.message.reply_text(
          f"🏆 {date.strftime('%d.%m.%Y')} — все умнички!",
          parse_mode="HTML"
        )
      return

    missed = [f"• @{m['username']}" if m['username'] else f"• ID {m['tg_id']}"
              for m in all_members if m["id"] in missed_ids]

    text = (
      f"📊 Статистика за <b>{date.strftime('%d.%m.%Y')}</b>\n\n"
  
      f"❌ Пропустили:\n" + ("\n".join(missed) if missed else "— никто")
    )

    if not is_bot:
      update.message.reply_text(text, parse_mode="HTML")
    else:
      bot.send_message(
        chat_id=CHAT_ID,
        text=text,
        parse_mode="HTML"
      )

  except Exception as e:
    bot.send_message(
      chat_id=ADMIN_TG_ID,
      text=f"⚠️ Ошибка в /day_stat: {e}",
    )