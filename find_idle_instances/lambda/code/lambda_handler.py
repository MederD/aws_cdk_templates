import logging
import os
from datetime import datetime
import boto3
from get_current_time_utc_and_local import get_current_time_utc_and_local
from get_start_and_end_times import get_start_and_end_times
from get_start_and_end_times_utc import get_start_and_end_times_utc
from get_all_running_instances import get_all_running_instances
from is_instance_idle import is_instance_idle
from send_report_to_sns import send_report_to_sns
from handle_exception import handle_exception

# Constants
CPU_IDLE_THRESHOLD = 10
NETWORK_IDLE_THRESHOLD = 5000
DISK_IO_THRESHOLD = 10
PERIOD = 3600

# Timezone and time range
TIMEZONE = 'America/Phoenix'
START_HOUR = 0
END_HOUR = 23

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    """
    AWS Lambda handler function that checks for idle EC2 instances and sends a report to an SNS topic if any are found.

    Parameters:
    - event: AWS Lambda event object
    - context: AWS Lambda context object

    Returns: None
    """
    try:
        # Get the current time in UTC and local timezones
        current_time_utc, current_time_local = get_current_time_utc_and_local()

        # Get the start and end times for the previous day in the local timezone
        start_time_local, end_time_local = get_start_and_end_times(current_time_local)

        # Convert the start and end times to UTC
        start_time_utc, end_time_utc = get_start_and_end_times_utc(start_time_local, end_time_local)

        # Get all running EC2 instances
        instances = get_all_running_instances()

        # Find idle instances and add their IDs to a list
        idle_instances = []
        for instance in instances:
            if is_instance_idle(instance.id, start_time_utc, end_time_utc, PERIOD):
                idle_instances.append(instance.id)
                logger.info(f"Idle instance found: {instance.id} between {start_time_local} and {end_time_local}")

        # Send the report to SNS topic if there are any idle instances
        if idle_instances:
            send_report_to_sns(idle_instances, start_time_local, end_time_local)
    except Exception as e:
        # Handle any exceptions that occur during execution
        handle_exception(e)
