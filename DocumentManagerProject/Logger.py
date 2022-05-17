# defines a wrapper around the aws cloudwatch client for logging
import boto3
import uuid
import time

from DocumentManagerProject.Constants import Constants

class Logger:

    # creates a wrapper for the CloudWatch logger
    # starts a new log stream for this component and tests posting a log to it
    def __init__(self, logGroup, componentName, boto3Session, awsRegion):
        self.logGroup = logGroup
        self.token = None
        self.cloudWatchClient = boto3Session.client("logs", region_name=awsRegion)
        try:
            self.logStreamName = self.logGroup + str(uuid.uuid4())
            self.cloudWatchClient.create_log_stream(logGroupName=logGroup,
                                                                     logStreamName=self.logStreamName)
            result = self.cloudWatchClient.put_log_events(logGroupName=self.logGroup,
                                                 logStreamName=self.logStreamName,
                                                 logEvents=[
                                                     {
                                                         'timestamp': int(time.time() * 1000),
                                                         'message': Constants.SUCCESS_SETUP_LOGGER.format(
                                                             componentName)
                                                     },
                                                 ]
                                                 )
            self.token = result["nextSequenceToken"]
        except Exception as e:
            print(Constants.FAILURE_SETUP_LOGGER.format(e))


    # wrapper for logging to the CloudWatch log stream set up for this component
    def log(self, logMessage):
        result = self.cloudWatchClient.put_log_events(
            logGroupName=self.logGroup,
            logStreamName=self.logStreamName,
            logEvents=[
                {
                    'timestamp': int(time.time() * 1000),
                    'message': logMessage
                },
            ],
            sequenceToken=self.token
        )
        self.token = result["nextSequenceToken"]

