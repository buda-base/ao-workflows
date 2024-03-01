#!/usr/bin/env python
"""
Creates a queue for notification on a bucket. Hardwired to manifest.bdrc.org and ManifestReadyToIntake
Change bucket and queue values to match your needs in __main__

Only needs run once for each queue. But is safe to run again with modified values.
REM that these json policies are the **only** ones stored, so deleting an element in them
will cause that element to be deleted in the bucket/SQS config.
"""
import json

import boto3

# Interested events - used by SQS and the permissions granter
# Take 2 - there's a lot going on in a bucket, all I want is the restores
event_list: [] = [
                  's3:ObjectRestore:*'
                  ]


def create_sqs_queue(queue_name, sqs: boto3.client = boto3.client('sqs')) -> str:
    """
    Creates an SQS queue with the specified name and returns the queue URL
    :param queue_name:
    :param sqs: client (optional)
    :return: queue URL
    """

    # Create an SQS queue
    response = sqs.create_queue(QueueName=queue_name)

    # Get the SQS queue URL
    queue_url = response['QueueUrl']

    print(f"SQS queue '{queue_name}' created with URL: {queue_url}")
    return queue_url


def create_s3_event_notification(tracked_bucket_name: str,
                                 queue_arn: str, s3: boto3.client = boto3.client('s3')) -> None:
    """
    Creates an S3 bucket event notification for the specified bucket and SQS queue
    :param tracked_bucket_name:
    :param queue_arn:
    :param s3: client (optional)
    :return:
    """

    # Define the S3 bucket event notification configuration

    event_notification_config = {
        'QueueConfigurations': [
            {
                'QueueArn': queue_arn,
                'Events': event_list

            }
        ]
    }

    # Set the S3 bucket event notification configuration
    s3.put_bucket_notification_configuration(
        Bucket=tracked_bucket_name,
        NotificationConfiguration=event_notification_config
    )

    print(f"S3 bucket event notification for '{tracked_bucket_name}' created with SQS queue ARN: {queue_arn}")


import boto3


def grant_s3_permissions_to_sqs_queue(watched_bucket_name: str,
                                      queue_url: str, sqs: boto3.client = boto3.client('sqs')) -> None:
    """
    Grants update notifications per
    :param watched_bucket_name:
    :param queue_url:
    :param sqs: client instance
    :return:
    """

    queue_arn = queue_url_to_arn(queue_url, sqs)

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
                        "aws:SourceArn": f"arn:aws:s3:*:*:{watched_bucket_name}"
                    }
                }
            }
        ]
    }

    # Attach the policy to the SQS queue
    # cough - ChatGPT suggested str(policy_document) - should be json.dumps(policy_document)
    sqs.set_queue_attributes(
        QueueUrl=queue_url,
        Attributes={
            'Policy': json.dumps(policy_document)
        }
    )

    print(f"Permissions granted for S3 bucket '{watched_bucket_name}' to send events to SQS queue '{queue_url}'")


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

    g_s3: boto3.client = boto3.client('s3')
    g_sqs: boto3.client = boto3.client('sqs')
    # Create an SQS queue
    intake_notification_queue_url: str = create_sqs_queue(queue_name, g_sqs)

    # Grant S3 permissions to send events to the SQS queue
    grant_s3_permissions_to_sqs_queue(bucket_name, intake_notification_queue_url, g_sqs)

    intake_notification_queue_arn = queue_url_to_arn( intake_notification_queue_url, g_sqs)
    # Create an S3 bucket event notification
    create_s3_event_notification(bucket_name, intake_notification_queue_arn , g_s3)
