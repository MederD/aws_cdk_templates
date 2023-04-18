import datetime
import logging

# Constants
TIMEZONE = 'America/Phoenix'
START_HOUR = 0
END_HOUR = 23

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_start_and_end_times(current_time_local):
    """
    Given a datetime object representing the current time in the local timezone,
    returns datetime objects representing the start and end times of the previous day
    in the local timezone.
    """
    try:
        current_time_local = current_time_local - datetime.timedelta(days=1)  # Subtract one day
        start_time_local = current_time_local.replace(hour=START_HOUR, minute=0, second=0, microsecond=0)
        end_time_local = current_time_local.replace(hour=END_HOUR, minute=0, second=0, microsecond=0)
        return start_time_local, end_time_local
    except Exception as e:
        logger.error(f"Error in get_start_and_end_times: {e}")
        raise e
