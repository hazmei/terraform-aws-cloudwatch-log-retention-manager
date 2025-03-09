import boto3
import os
import logging

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, format='%(message)s')

def lambda_handler(event, context):
    default_region = os.environ.get('AWS_REGION', 'us-east-1')
    retain_days = int(os.environ.get('RETAIN_DAYS', '30'))
    log_groups_to_set = os.environ.get('LOG_GROUPS_TO_SET', [])

    logger.info("Checking for logs with names: %s", log_groups_to_set)
    logger.info("Setting logs to %s days", retain_days)

    if log_groups_to_set != []:
        log_groups_to_set = log_groups_to_set.split(",")

    session = boto3.Session()
    client = session.client('ec2', region_name=default_region)

    for region_dict in client.describe_regions()['Regions']:
        region = region_dict['RegionName']
        logger.info("Checking %s region", region)
        logs = session.client('logs', region_name=region)
        paginator = logs.get_paginator('describe_log_groups')

        for page in paginator.paginate():
            for log_group in page['logGroups']:
                log_group_name = log_group['logGroupName']
                # If LOG_GROUPS_TO_SET is configured, it will
                # search for log group that matches it or a subset
                # else look through all logs and set the retentionInDays
                # if it is not set
                if (len(log_groups_to_set) == 0 or any(log_group_to_set in log_group_name for log_group_to_set in log_groups_to_set)) and ('retentionInDays' not in log_group):
                    logger.info("Setting %s logs %s to %s days", region, log_group_name, retain_days)
                    response = logs.put_retention_policy(
                        logGroupName=log_group_name,
                        retentionInDays=retain_days
                    )

    logger.info("Checking completed")
    return 'CloudWatchLogRetention.Success'
