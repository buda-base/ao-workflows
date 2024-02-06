#!/usr/bin/env python

import boto3



def create_sqs_queue(queue_name) -> str:
    """
    Creates an SQS queue with the specified name and returns the queue URL
    :param queue_name:
    :return: queue URL
    """
    sqs = boto3.client('sqs')

    # Create an SQS queue
    response = sqs.create_queue(QueueName=queue_name)

    # Get the SQS queue URL
    queue_url = response['QueueUrl']

    print(f"SQS queue '{queue_name}' created with URL: {queue_url}")
    return queue_url


def create_s3_event_notification(bucket_name: str, queue_url: str):
    s3 = boto3.client('s3')

    # Define the S3 bucket event notification configuration
    completed_
                 = ['s3:ObjectCreated:*',
                  's3:ObjectUpdated:*',
                  's3:ObjectUploaded:*',
                  's3:ObjectRestore:Completed'
                  ]
    event_notification_config = {
        'QueueConfigurations': [
            {
                'QueueArn': queue_arn,
                'Events': completed_
                
            }
        ]
    }

    # Set the S3 bucket event notification configuration
    s3.put_bucket_notification_configuration(
        Bucket=bucket_name,
        NotificationConfiguration=event_notification_config
    )

    print(f"S3 bucket event notification for '{bucket_name}' created with SQS queue ARN: {queue_arn}")


import boto3


def grant_s3_permissions_to_sqs_queue(bucket_name: str, queue_url: str) -> None:
    """
    Grants update notifications per
    :param bucket_name: 
    :param queue_url: 
    :return: 
    """
    s3 = boto3.client('s3')
    sqs = boto3.client('sqs')

    queue_arn = queue_url_to_arn(queue_url, sqs)

    # Define the S3 bucket event notification configuration
    event_notification_config = {
        'QueueConfigurations': [
            {
                'QueueArn': queue_arn,
                'Events': ['s3:ObjectCreated:*']
            }
        ]
    }

    # Set the S3 bucket event notification configuration
    s3.put_bucket_notification_configuration(
        Bucket=bucket_name,
        NotificationConfiguration=event_notification_config
    )

    print(f"S3 bucket event notification for '{bucket_name}' created with SQS queue ARN: {queue_arn}")

    # Define the policy that grants S3 permissions to send events to the SQS queue
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "s3.amazonaws.com"
                },
                "Action": "sqs:SendMessage",
                "Resource": queue_arn,
                "Condition": {
                    "ArnLike": {
                        "aws:SourceArn": f"arn:aws:s3:::{bucket_name}"
                    }
                }
            }
        ]
    }

    # Attach the policy to the SQS queue
    sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            'Policy': str(policy_document)
        }
    )

    print(f"Permissions granted for S3 bucket '{bucket_name}' to send events to SQS queue '{queue_url}'")


def queue_url_to_arn(queue_url: str, sqs: boto3.client = boto3.client('sqs')) -> str:
    """
    Converts an SQS queue URL to an ARN
    :param queue_url: 
    :param sqs: 
    :return: Queue's ARN
    """
    # Get the SQS queue attributes to retrieve the queue ARN
    queue_attributes = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=['QueueArn'])
    queue_arn = queue_attributes['Attributes']['QueueArn']
    return queue_arn


if __name__ == "__main__":
    # Specify your AWS S3 bucket name and SQS queue name
    bucket_name = 'manifest.bdrc.org'
    queue_name = 'ManifestReadyToIntake'

    # Create an SQS queue
    queue_arn = create_sqs_queue(queue_name)

    # Grant S3 permissions to send events to the SQS queue
    grant_s3_permissions_to_sqs_queue(bucket_name, queue_arn)

    # Create an S3 bucket event notification
    create_s3_event_notification(bucket_name, queue_arn)
