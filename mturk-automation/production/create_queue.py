import boto3
#from boto3 import client
client = boto3.client(service_name='sqs')


mypolicy = {
    "Version": "2008-10-17",
    "Id":
    "arn:aws:sqs:us-east-1:ID:mturkNotificationQueue/MTurkOnlyPolicy",
    "Statement": [
           {
               "Sid": "MTurkOnlyPolicy",
               "Effect": "Allow",
               "Principal": {
                      "AWS": "arn:aws:iam::ID:user/MTurk-SQS"
               },
               "Action": "SQS:SendMessage",
               "Resource":
               "arn:aws:sqs:us-east-1:ID:mturkNotificationQueue"
           }
    ]
}

myqueue = client.create_queue(QueueName='mturkNotificationQueue')
print(myqueue['QueueUrl'])
