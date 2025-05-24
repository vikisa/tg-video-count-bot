from datetime import datetime
from zoneinfo import ZoneInfo

def get_moscow_today_date(input_str: str = None):
    if input_str:
        try:
            return datetime.strptime(input_str, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Некорректный формат даты. Используй дд.мм.гггг")
    else:
        return datetime.now(ZoneInfo("Europe/Moscow")).date()