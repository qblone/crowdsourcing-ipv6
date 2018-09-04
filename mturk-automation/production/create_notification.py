import boto3

client = boto3.client(service_name='sqs')

mturk = boto3.client(service_name='mturk',
                     region_name='us-east-1')

mypolicy = {
    "Version": "2008-10-17",
    "Id":
    "arn:aws:sqs:us-east-1:NOTID:mturkNotificationQueue/MTurkOnlyPolicy",
    "Statement": [
           {
               "Sid": "MTurkOnlyPolicy",
               "Effect": "Allow",
               "Principal": {
                      "AWS": "arn:aws:iam::IAMID:user/MTurk-SQS"
               },
               "Action": "SQS:SendMessage",
               "Resource":
               "arn:aws:sqs:us-east-1:NOTID:mturkNotificationQueue"
           }
    ]
}

myqueue = client.create_queue(QueueName='NotificationQueue')
print(myqueue['QueueUrl'])


# Get the HITTypeID
hits = mturk.list_hits()

# print(hits)
mHITTypeID = hits['HITs'][0]['HITTypeId']


def getHitsType():
  all_hit_types = set()
  hits = mturk.list_hits()
  for hit in hits['HITs']:
    all_hit_types.add(hit['HITTypeId'])
  marker = hits['NextToken']
  if marker:
    while True:
      hits = mturk.list_hits(NextToken=marker)
      for hit in hits['HITs']:
        all_hit_types.add(hit['HITTypeId'])
      if 'NextToken' in hits:
        marker = hits['NextToken']
      else:
        break
  return all_hit_types


hit_types = getHitsType()


for mHITTypeID in hit_types:
  #mHITTypeID = hit['HITTypeId']
  print("Creating notification for {}".format(mHITTypeID))
  response = mturk.update_notification_settings(
      HITTypeId=mHITTypeID,
      Notification={
          'Destination': myqueue['QueueUrl'],
          'Transport': 'SQS',
          'Version': '2006-05-05',
          'EventTypes': [
              'AssignmentSubmitted',

          ]
      },

  )
