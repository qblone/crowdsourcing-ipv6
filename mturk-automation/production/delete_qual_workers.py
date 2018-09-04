import boto3
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
import json
from pprint import pprint


mturk = boto3.client(service_name='mturk', region_name='us-east-1')

response = mturk.list_qualification_types(
    Query='Auto',
    MustBeRequestable=True,
    MustBeOwnedByCaller=True,
)

QualID = ''
if response['QualificationTypes'][0]:
    QualID = response['QualificationTypes'][0]['QualificationTypeId']
else:
    print("There is no qualification, please create one first")
    raise()


print(QualID)

workers = mturk.list_workers_with_qualification_type(QualificationTypeId=QualID)

for worker in workers['Qualifications']:
    print(worker['WorkerId'])
    mturk.disassociate_qualification_from_worker(
        WorkerId=worker['WorkerId'],
        QualificationTypeId=QualID,
        Reason='Starting a new batch, you can now take part in the  experiment again.'
    )
marker = workers['NextToken']
if marker:
    while True:
        workers = mturk.list_workers_with_qualification_type(QualificationTypeId=QualID, NextToken=marker)
        for worker in workers['Qualifications']:
            print(worker['WorkerId'])
            mturk.disassociate_qualification_from_worker(
                WorkerId=worker['WorkerId'],
                QualificationTypeId=QualID,
                Reason='Starting a new batch, you can now take part in the  experiment again.'
            )
        if 'NextToken' in workers:
            marker = workers['NextToken']
        else:
            break


print(marker)
