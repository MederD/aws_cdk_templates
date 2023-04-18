import datetime
import pytz
import logging

# Constants
TIMEZONE = 'America/Phoenix'

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_current_time_utc_and_local():
    """
    Get the current time in UTC and the local timezone.

    Returns:
        A tuple containing the current time in UTC and the local timezone.
    """
    try:
        current_time_utc = datetime.datetime.utcnow()
        current_time_local = current_time_utc.replace(tzinfo=pytz.utc).astimezone(pytz.timezone(TIMEZONE))
        return current_time_utc, current_time_local
    except Exception as e:
        logger.error(f"Error getting current time: {str(e)}")
        raise e
