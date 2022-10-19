from email.message import EmailMessage
import boto3
sns = boto3.client("sns")
response = sns.publish(
    TopicArn="arn:aws:sns:us-east-1:159322282447:Devops",
    Message="Hello World!"
)

print(response)