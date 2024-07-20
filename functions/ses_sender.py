import boto3

mail = boto3.client('ses')

def send_mail(token):
    sender = "no-reply@example.com"
    recipient = "aiman.zaidi.dev@gmail.com"
    subject = "Test Email from Boto3"
    body_text = "Here is your login token: {}\nPlease send it to bot to get authenticated.".format(token)

    message = {
        'Body': {
            'Text': {
                'Charset': 'UTF-8',
                'Data': body_text
            }
        },
        'Subject': {
            'Charset': 'UTF-8',
            'Data': subject
        },
        'Sender': sender
}

    try:
        response = mail.send_email(
            Destination={
                'ToAddresses': [
                    recipient
                ]
            },
            Message=message,
            Source=sender
        )
        print("Email sent successfully. Message ID:", response['MessageId'])
    except Exception as e:
        print("Error sending email:", e)
