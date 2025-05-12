from datetime import datetime, date
from telegram import Update
from telegram.ext import CallbackContext
from db.marathon_queries import get_active_marathon_by_chat
from db.marathon_members import get_all_members_of_marathon
from db.day_results import get_members_who_sent_video
from db.member_queries import get_member_by_tg_id

YOUR_TG_ID = 248146008

def day_stat_command(update: Update, context: CallbackContext):
    chat = update.effective_chat
    user = update.effective_user

    member = get_member_by_tg_id(user.id)
    if not (member and member["is_admin"]) and user.id != YOUR_TG_ID:
        update.message.reply_text("⛔ Только админ может запрашивать статистику.")
        return

    # 📅 Дата: из аргумента или сегодня
    if context.args:
        try:
            selected_date = datetime.strptime(context.args[0], "%d.%m.%Y").date()
        except ValueError:
            update.message.reply_text("❌ Неверный формат даты. Используй: /day_stat дд.мм.гггг")
            return
    else:
        selected_date = date.today()

    marathon = get_active_marathon_by_chat(chat.id)
    if not marathon:
        update.message.reply_text("❌ Активный марафон не найден.")
        return

    if selected_date < marathon["start_date"]:
        update.message.reply_text(
            f"❌ Статистика за {selected_date.strftime('%d.%m.%Y')} невозможна — марафон ещё не начался.",
            parse_mode="HTML"
        )
        return

    try:
        all_members = get_all_members_of_marathon(marathon["id"])
        sent_ids = get_members_who_sent_video(marathon["id"], selected_date)
        all_ids = {m["id"] for m in all_members}
        missed_ids = all_ids - sent_ids

        # 🎉 если все сдали
        if not missed_ids and sent_ids:
            update.message.reply_text(
                f"🏆 {selected_date.strftime('%d.%m.%Y')} — все умнички!",
                parse_mode="HTML"
            )
            return

        sent = [f"• @{m['username']}" if m['username'] else f"• ID {m['tg_id']}"
                for m in all_members if m["id"] in sent_ids]
        missed = [f"• @{m['username']}" if m['username'] else f"• ID {m['tg_id']}"
                  for m in all_members if m["id"] in missed_ids]

        text = (
            f"📊 Статистика за <b>{selected_date.strftime('%d.%m.%Y')}</b>\n\n"
            
            f"❌ Пропустили:\n" + ("\n".join(missed) if missed else "— никто")
        )

        update.message.reply_text(text, parse_mode="HTML")

    except Exception as e:
        context.bot.send_message(YOUR_TG_ID, f"⚠️ Ошибка в /day_stat: {e}")
