import re
from datetime import datetime
from django.db.models import Q

def filter_by_date(objects, date):
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if date is not None:
        if len(date) == 11 and date_pattern.match(date[1:]):
            operator = date[0]
            date_value = datetime.strptime(date[1:], "%Y-%m-%d").date()
            if operator == "=":
                objects = objects.filter(start_date=date_value)
            elif operator == "<":
                objects = objects.filter(start_date__lt=date_value)
            elif operator == ">":
                objects = objects.filter(start_date__gt=date_value)
    return objects

def filter_by_username(objects, username):
    if username is not None:
        objects = objects.filter(
            Q(student_player__username__icontains=username) |
            Q(teacher_player__username__icontains=username)
        )
    return objects

def filter_by_length(objects, length):
    if length is not None:
        if len(length) >= 2:
            operator = length[0]
            numeric_value = int(length[1:])

            if operator == "<":
                objects = objects.filter(lenght_in_sec__lt=numeric_value)
            elif operator == ">":
                objects = objects.filter(lenght_in_sec__gt=numeric_value)
    return objects

def filter_by_winner(objects, winner):
    if winner is not None:
        if winner == "student" or winner == "teacher":
            objects = objects.filter(winner=winner)
    return objects
