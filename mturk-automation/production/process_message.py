import boto3
from pprint import pprint
sqs = boto3.resource('sqs')
queue = sqs.get_queue_by_name(QueueName='NotificationQueue')
import json
from update_qualification import UpdateQualification
from updateDB import UpDataDB

update_qual = UpdateQualification()
update_db = UpDataDB()
while True:
    for message in queue.receive_messages():
        if message:
            notification = json.loads(message.body)
            pprint(notification)
            worker = notification['CustomerId'].strip()
            action = notification['Events'][0]['EventType']
            hit_id = notification['Events'][0]['HITId']
            print("Worker{}".format(worker))
            print("Action ", action)
            if action == "AssignmentAccepted":
                print("Adding qualification for {}.".format(worker))
            if action == "AssignmentSubmitted":
                update_db.update_from_platform(hit_id, worker)

            message.delete()
