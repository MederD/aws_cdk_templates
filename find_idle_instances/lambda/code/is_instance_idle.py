import boto3
import logging
from get_idle_metrics_thresholds import get_idle_metrics_thresholds

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def is_instance_idle(instance_id, start_time_utc, end_time_utc, period):
    """
    Check if an EC2 instance is idle based on the defined thresholds for CPU, network packets in/out and disk I/O.

    Args:
        instance_id (str): The ID of the instance to check.
        start_time_utc (datetime): The start time in UTC to check for metrics.
        end_time_utc (datetime): The end time in UTC to check for metrics.
        period (int): The period in seconds for the metric data.

    Returns:
        bool: True if the instance is idle, False otherwise.
    """
    cloudwatch = boto3.client('cloudwatch')
    idle_metrics_thresholds = get_idle_metrics_thresholds()

    for metric_name, threshold in idle_metrics_thresholds.items():
        try:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName=metric_name,
                Dimensions=[
                    {
                        'Name': 'InstanceId',
                        'Value': instance_id
                    },
                ],
                StartTime=start_time_utc,
                EndTime=end_time_utc,
                Period=period,
                Statistics=['SampleCount', 'Average'],
                Unit='Percent' if metric_name == 'CPUUtilization' else 'Count'
            )
        except Exception as e:
            logger.error(f"Failed to get {metric_name} metric for instance {instance_id}: {e}")
            continue

        if response['Datapoints']:
            datapoint = response['Datapoints'][0]
            average_value = datapoint['Average']

            if average_value > threshold:
                return False

    return True
