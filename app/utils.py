from datetime import datetime


def is_new_quarter_hour():
    now = datetime.now()
    return now.minute % 15 == 0 and now.second == 0
