import boto3
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
from boto.mturk.price import Price
import boto.mturk.qualification as mtqu
from pprint import  pprint





#from boto3 import client
client = boto3.client(service_name ='sqs')
#mturk = boto3.client('mturk')
mturk = boto3.client(service_name = 'mturk', 
                     region_name='us-east-1')






questionSampleFile = open("external_hit.question", "r")
questionSample = questionSampleFile.read()

# Create a qualification with Locale In('US', 'CA') requirement attached
# Get qualification
qualifications = mturk.list_qualification_types(
            Query='Auto',
            MustBeRequestable=True,
            MustBeOwnedByCaller=True,
)


qualification = qualifications['QualificationTypes'][0]['QualificationTypeId']

localRequirements = [{
        'QualificationTypeId': qualification,
        'Comparator': 'DoesNotExist',
        'RequiredToPreview': False
}]

# Create the HIT 
def create_hits(num_of_hits):
    for _ in range(num_of_hits):
        response = mturk.create_hit(
            MaxAssignments = 1,
            LifetimeInSeconds = 604800,
            AssignmentDurationInSeconds = 3600,
            Reward ='0.01',
            Title= 'Chose the color of the ball to test if you have IPV6',
            Keywords = 'easy, research',
            Description = 'The participants have to select the color of the ball that appears on the screen. The red ball means they have been assigned a new version of the IP addressing (IPv6) from their Internet providers. In the case of the blue ball, they are using IPv4. Once you complete one task you can NOT work on subsequent tasks by this requester.',
            Question = questionSample,
            QualificationRequirements = localRequirements
    )
    return response
#response = create_hits_from_id()
response = create_hits(50)
pprint(response)
# The response included several fields that will be helpful later
hit_type_id = response['HIT']['HITTypeId']
hit_id = response['HIT']['HITId']
print ("Your HIT has been created. You can see it at this link:")
print("https://workersandbox.mturk.com/mturk/preview?groupId={}".format(hit_type_id))
print ("Your HIT ID is: {}".format(hit_id))
