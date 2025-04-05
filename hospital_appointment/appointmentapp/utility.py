from datetime import datetime
from django.utils import timezone

def parse_datetime(datetime_str):
    """Convert string to timezone-aware datetime"""
    if not datetime_str:
        raise ValueError('Datetime string is required')
    
    try:
        naive_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        return timezone.make_aware(naive_datetime)
    except ValueError:
        raise ValueError('Invalid datetime format. Use YYYY-MM-DD HH:MM:SS')    