import logging

# Constants
CPU_IDLE_THRESHOLD = 10
NETWORK_IDLE_THRESHOLD = 5000
DISK_IO_THRESHOLD = 10

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_idle_metrics_thresholds():
    """
    Returns a dictionary of idle metric thresholds for CloudWatch metrics.

    Returns:
        dict: Dictionary of idle metric thresholds.
    """
    try:
        idle_metrics_thresholds = {
            'CPUUtilization': CPU_IDLE_THRESHOLD,
            'NetworkPacketsIn': NETWORK_IDLE_THRESHOLD,
            'NetworkPacketsOut': NETWORK_IDLE_THRESHOLD,
            'DiskReadOps': DISK_IO_THRESHOLD,
            'DiskWriteOps': DISK_IO_THRESHOLD
        }
        return idle_metrics_thresholds
    except Exception as e:
        logger.error(f"Error in get_idle_metrics_thresholds: {e}")
        raise e
