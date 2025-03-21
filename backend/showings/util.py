from datetime import datetime


def get_current_year():
    return datetime.now().strftime("%Y")


def get_current_month():
    return datetime.now().strftime("%m")


def get_first_non_empty(*values):
    return next((v for v in values if v), "")
