import boto3, logging, time, datetime
from datetime import datetime, timedelta

class LogWrapper:
    def __init__(self, log_client, instance = None):
        self.log_client = log_client
        self.instance = instance

        self.logger = logging.getLogger()
        logging.basicConfig()
        self.logger.setLevel(logging.INFO)

    @classmethod
    def from_resource(cls):
        log_client = boto3.client('logs')
        return cls(log_client)

    def query_logs(self, logName, query_string):
        try:
            self.logger.info(" --- Start query --- ")

            result = self.log_client.start_query(
                logGroupName = logName,
                startTime = int((datetime.today() - timedelta(minutes = 10)).timestamp()),
                endTime = int(datetime.now().timestamp()),
                queryString = query_string,
                limit = 100
            )

            self.logger.info(' --- Sleeping --- ')

            tries = 30
            total_sleep_time = 0
            self.logger.info(' --- Getting results --- ')
            response = self.log_client.get_query_results(
                queryId = result['queryId']
            )
            while(not response['results'] and tries > 0):
                response = self.log_client.get_query_results(
                    queryId = result['queryId']
                )

                time.sleep(0.5)
                total_sleep_time += 0.5
                tries -= 1

            if(not response['results']):
                raise Exception(" --- No results found --- ")

            self.logger.info(" --- Function slept for a total of %s seconds.--- ", total_sleep_time)
            self.logger.info(' --- Number of results: %s --- ' % (len(response['results'])))

            ips = [record['value'] for sublist in response['results'] for record in sublist if record['field'] == 'httpRequest.clientIp']
            return tuple(ips)

        except Exception:
            self.logger.error(" --- Error! --- ")
            raise
