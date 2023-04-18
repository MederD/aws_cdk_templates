import datetime
import pytz
import logging

logger = logging.getLogger()

# Constants
TIMEZONE = 'America/Phoenix'

def get_start_and_end_times_utc(start_time_local: datetime.datetime, end_time_local: datetime.datetime) -> tuple:
    """
    Converts the start and end times from local timezone to UTC timezone.

    :param start_time_local: The local start time as datetime object.
    :param end_time_local: The local end time as datetime object.
    :return: The start and end times as datetime objects in UTC timezone.
    """
    try:
        start_time_local = start_time_local - datetime.timedelta(days=1)
        end_time_local = end_time_local - datetime.timedelta(days=1)
        start_time_utc = start_time_local.astimezone(pytz.utc).replace(tzinfo=None)
        end_time_utc = end_time_local.astimezone(pytz.utc).replace(tzinfo=None)
        return start_time_utc, end_time_utc
    except Exception as e:
        logger.error(f"An error occurred while converting start and end times to UTC timezone: {e}")
        raise e
