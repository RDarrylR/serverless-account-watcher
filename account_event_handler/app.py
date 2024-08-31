from aws_lambda_powertools import Logger, Tracer, Metrics
import boto3
import requests
import json
import os
import traceback

logger = Logger()
tracer = Tracer()
metrics = Metrics(namespace="AccountEventHandler")


@tracer.capture_method
def parse_event(event):
    """Parse details of event"""

    result = ""
    eventName  = "UNKNOWN EVENT"
    eventDetail = event.get('detail')
    if eventDetail:
        eventName = eventDetail.get('eventName')
        
        try:
            match eventName:
                
                # S3 events
                case "DeleteBucket":
                    result = f"Bucket \"{eventDetail.get('requestParameters').get('bucketName')}\" was deleted by \"{eventDetail.get('userIdentity').get('type')}\" \"{eventDetail.get('userIdentity').get('arn')}\""
                case "PutBucketPolicy":
                    result = f"Bucket \"{eventDetail.get('requestParameters').get('bucketName')}\" policy added by \"{eventDetail.get('userIdentity').get('type')}\" \"{eventDetail.get('userIdentity').get('arn')}\""
                case "DeleteBucketPolicy":
                    result = f"Bucket \"{eventDetail.get('requestParameters').get('bucketName')}\" policy deleted by \"{eventDetail.get('userIdentity').get('type')}\" \"{eventDetail.get('userIdentity').get('arn')}\""

                # IAM events
                case "CreateAccessKey":
                    result = f"Access Key \"{eventDetail.get('responseElements').get('accessKey').get('accessKeyId')}\" for user \"{eventDetail.get('requestParameters').get('userName')}\" created by \"{eventDetail.get('userIdentity').get('type')}\" \"{eventDetail.get('userIdentity').get('arn')}\""
                case "DeleteAccessKey":
                    result = f"Access Key \"{eventDetail.get('requestParameters').get('accessKeyId')}\" for user \"{eventDetail.get('requestParameters').get('userName')}\" deleted by \"{eventDetail.get('userIdentity').get('type')}\" \"{eventDetail.get('userIdentity').get('arn')}\""
                case "UpdateRole":
                    result = f"Role \"{eventDetail.get('requestParameters').get('roleName')}\" updated by \"{eventDetail.get('userIdentity').get('type')}\" \"{eventDetail.get('userIdentity').get('arn')}\""
                case "DeleteRole":
                    result = f"Role \"{eventDetail.get('requestParameters').get('roleName')}\" deleted by \"{eventDetail.get('userIdentity').get('type')}\" \"{eventDetail.get('userIdentity').get('arn')}\""
 
                # Console Login events    
                case "ConsoleLogin":
                    result = f"Root user console login from IP: \"{eventDetail.get('sourceIPAddress')}\""                    
                    
                # Default generic event    
                case _:
                    result = eventDetail
        except:
            result = event
    return eventName, result

@tracer.capture_method
def send_slack_message(payload, webhook):
    """Send Slack message to passed in URL
    """
    logger.debug(f"payload={payload} webhook={webhook}")
    headers = {'Content-Type': 'application/json'}
    return requests.post(webhook, data=json.dumps(payload), headers=headers)

@tracer.capture_method
def publish_to_sns(subject, message, topic):
    logger.debug(f"subject={subject} message={message} topic={topic}")
    # Send message to SNS
    sns_client = boto3.client('sns')
    return sns_client.publish(TopicArn=topic, Subject=subject, Message=message)
    
    
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    try:   
        
        SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']
        SLACK_WEBHOOK_URL = os.environ['SLACK_WEBHOOK_URL'] 
        
        logger.debug(f"SNS_TOPIC_ARN={SNS_TOPIC_ARN}")    
        logger.debug(f"SLACK_WEBHOOK_URL={SLACK_WEBHOOK_URL}")       

        event_name, event_detail = parse_event(event)
        slack_msg = f"{event_name}: {event_detail}"
        logger.debug(f"slack_msg={slack_msg}")
        
        slack_response = send_slack_message({"text": slack_msg}, SLACK_WEBHOOK_URL)
        logger.debug(f"slack_response={slack_response}")
        
        sns_subject = event_name
        sns_msg = event_detail
        sns_response = publish_to_sns(sns_subject, sns_msg, SNS_TOPIC_ARN)
        logger.debug(f"sns_response={sns_response}") 
                
                
    except Exception as ex:
        logger.exception("Exception hit")
        raise RuntimeError("Cannot prcocess event") from ex
