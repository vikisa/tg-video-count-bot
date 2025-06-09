from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext
from db.member_queries import get_member_by_tg_id
from utils.get_moscow_today import get_moscow_today_date
from utils.consts import ADMIN_TG_ID
from utils.day_stat import get_day_stat
from typing import TypedDict

class ReplyDict(TypedDict):
    update: Update
    context: CallbackContext

def day_stat_command(update: Update, context: CallbackContext):
    user = update.effective_user

    member = get_member_by_tg_id(user.id)
    if not (member and member["is_admin"]) and user.id != ADMIN_TG_ID:
        update.message.reply_text("⛔ Только админ может запрашивать статистику.")
        return

    if context.args:
        try:
            selected_date = datetime.strptime(context.args[0], "%d.%m.%Y").date()
        except ValueError:
            update.message.reply_text("❌ Неверный формат даты. Используй: /day_stat дд.мм.гггг")
            return
    else:
        selected_date = get_moscow_today_date()

    reply: ReplyDict = {
        "update": update,
        "context": context
    }
    get_day_stat(selected_date, reply, False)
