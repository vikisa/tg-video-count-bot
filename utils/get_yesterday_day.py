from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def get_yesterday_date():
  moscow_now = datetime.now(ZoneInfo("Europe/Moscow"))
  yesterday = moscow_now.date() - timedelta(days=1)
  return yesterday