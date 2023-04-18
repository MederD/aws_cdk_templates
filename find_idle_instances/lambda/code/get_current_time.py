import datetime
import logging
import pytz

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TIMEZONE = 'America/Phoenix'

def get_current_time_utc_and_local():
    """
    Returns the current time in UTC and local timezone.

    Returns:
    datetime.datetime: The current time in UTC.
    datetime.datetime: The current time in the local timezone.
    """
    try:
        current_time_utc = datetime.datetime.utcnow()
        current_time_local = current_time_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIMEZONE))
        return current_time_utc, current_time_local
    except Exception as e:
        logger.error(f"Error in get_current_time_utc_and_local: {e}")
        raise e
