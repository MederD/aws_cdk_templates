import boto3
import os
import json
import io
import datetime
import pytz
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
from is_instance_idle import is_instance_idle
from get_metric_statistics import get_metric_statistics

# Constants
CPU_IDLE_THRESHOLD = 10
NETWORK_IDLE_THRESHOLD = 5000
DISK_IO_THRESHOLD = 10
PERIOD = 3600

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def get_datapoint_value(response, statistic):
    """
    Extracts the value of the specified statistic from the first datapoint in a CloudWatch response.

    Args:
    - response (dict): The CloudWatch response containing the datapoints.
    - statistic (str): The name of the statistic to extract (e.g., 'Average', 'Sum').

    Returns:
    - float: The value of the specified statistic, or None if no datapoints were returned.
    """
    if response['Datapoints']:
        return response['Datapoints'][0][statistic]
    else:
        return 0

def send_report_to_sns(idle_instances, start_time_local, end_time_local):
    sns = boto3.client('sns')
    sns_topic_arn = os.environ['SNS_TOPIC_ARN']

    # Generate a report for each idle instance
    for instance_id in idle_instances:
        start_time_utc = start_time_local.astimezone(pytz.utc)
        end_time_utc = end_time_local.astimezone(pytz.utc)

        report_lines = []
        report_lines.append(f"Idle instance found: {instance_id} between {start_time_local} and {end_time_local}")

        for hour in range(0, 24):
            timestamp = start_time_local.replace(hour=hour, minute=0, second=0, microsecond=0)

            if is_instance_idle(instance_id, start_time_utc, end_time_utc, PERIOD):
                cpu_utilization_response = get_metric_statistics(instance_id, 'CPUUtilization', start_time_utc, end_time_utc, PERIOD, ['SampleCount', 'Average'], 'Percent')
                network_packets_in_response = get_metric_statistics(instance_id, 'NetworkPacketsIn', start_time_utc, end_time_utc, PERIOD, ['SampleCount', 'Average'], 'Count')
                network_packets_out_response = get_metric_statistics(instance_id, 'NetworkPacketsOut', start_time_utc, end_time_utc, PERIOD, ['SampleCount', 'Average'], 'Count')

                cpu_utilization_average = get_datapoint_value(cpu_utilization_response, 'Average')
                network_packets_in_sum = get_datapoint_value(network_packets_in_response, 'Sum')
                network_packets_out_sum = get_datapoint_value(network_packets_out_response, 'Sum')

                report_lines.append(f"{timestamp.strftime('%Y-%m-%d-%H.%M.%S')} - Average CPU: {cpu_utilization_average:.1f}%, NetworkPacketsIn: {network_packets_in_sum:.0f}, NetworkPacketsOut: {network_packets_out_sum:.0f}")

        # Join all report lines into a message
        message = "\n".join(report_lines)

        # Send the message to SNS
        response = sns.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject=f"Idle Instance {instance_id} Report",
        )

        logger.info(f"Report for instance {instance_id} sent to SNS with message ID: {response['MessageId']}")
