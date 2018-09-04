'''
This script gets the workers which has completed the task and updates the
database accordingly. I wrote the script because bug in my initial code which 
resulted in wrong workerid being captured

'''
import sqlite3
import boto3
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
import json
from pprint import pprint
from collections import defaultdict

mturk = boto3.client(service_name='mturk', region_name='us-east-1')


# Count each category of HITs
counter = defaultdict(int)
hits = mturk.list_hits()

print(type(hits.keys()))
print(hits['NextToken'])
print(len(hits))
for hit in hits['HITs']:
    counter['totalHITS'] += 1
    response = mturk.list_assignments_for_hit(HITId=hit['HITId'],)
    assignments = response['Assignments']
    for assignment in assignments:
        pprint(assignment['AssignmentId'])
        print(assignment['AssignmentStatus'])
        if not assignment['AssignmentStatus'] == "Approved":
            mturk.approve_assignment(AssignmentId=assignment['AssignmentId'])

marker = hits['NextToken']
if marker:
    while True:
        hits = mturk.list_hits(NextToken=marker)
        for hit in hits['HITs']:
            counter['totalHITS'] += 1
            response = mturk.list_assignments_for_hit(HITId=hit['HITId'],)
            assignments = response['Assignments']
            for assignment in assignments:
                if not assignment['AssignmentStatus'] == "Approved":
                    mturk.approve_assignment(AssignmentId=assignment['AssignmentId'])
                counter[assignment['AssignmentStatus']] += 1
        if 'NextToken' in hits:
            marker = hits['NextToken']
        else:
            break
print(counter)
