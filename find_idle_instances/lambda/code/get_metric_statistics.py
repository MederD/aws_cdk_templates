import boto3
import datetime
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_metric_statistics(instance_id, metric_name, start_time_utc, end_time_utc, period, statistics, unit):
    """
    Gets the CloudWatch statistics for the specified EC2 instance and metric.

    Args:
    - instance_id (str): The ID of the EC2 instance to get the metric statistics for.
    - metric_name (str): The name of the CloudWatch metric to get the statistics for.
    - start_time_utc (datetime): The start time for the CloudWatch query, in UTC.
    - end_time_utc (datetime): The end time for the CloudWatch query, in UTC.
    - period (int): The period for the CloudWatch query, in seconds.
    - statistics (list): The statistics to retrieve for the metric.
    - unit (str): The unit for the metric.

    Returns:
    - dict: A dictionary containing the CloudWatch statistics for the specified EC2 instance and metric.
    """
    cloudwatch = boto3.client('cloudwatch')

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
        Statistics=statistics,
        Unit=unit
    )

    datapoints = response.get('Datapoints', [])
    logger.info(f"Got metric statistics for instance {instance_id} and metric {metric_name}: {datapoints}")

    return response
