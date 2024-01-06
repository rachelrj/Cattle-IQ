import boto3
from botocore.exceptions import ClientError

ses = boto3.client('ses', region_name='us-west-2')
sender = "errors@cattleiq.io"
recipients = ["rachelrj29@gmail.com", "shanesjoyce@gmail.com", "rachel@cattleiq.io", "shane@cattleiq.io"] 
subject = "Error: CattleIQ"

def send_error_email(message):
    ses = boto3.client('ses', region_name='us-west-2')
    sender = "errors@cattleiq.io"
    recipients = ["rachelrj29@gmail.com", "shanesjoyce@gmail.com", "rachel@cattleiq.io", "shane@cattleiq.io"] 
    subject = "Error: CattleIQ"
    body_text = f"{message}"
    body_html = f"<html><head></head><body><h1>Error</h1><p>{message}</p></body></html>"
    try:
        response = ses.send_email(
            Destination={'ToAddresses': recipients},
            Message={
                'Body': {
                    'Html': {'Charset': "UTF-8", 'Data': body_html},
                    'Text': {'Charset': "UTF-8", 'Data': body_text},
                },
                'Subject': {'Charset': "UTF-8", 'Data': subject},
            },
            Source=sender,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:", response['MessageId'])