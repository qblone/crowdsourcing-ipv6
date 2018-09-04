from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views import View
from django.http import HttpResponse
from testipv6.models import IPAddresses as IPmodel
from .forms import submitData
import logging
import boto3


# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.


def _get_form(request, formcls, prefix):
    data = request.POST if prefix in request.POST else None
    return formcls(data, prefix=prefix)


class MyView(TemplateView):

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        platform_ = getPlatform(request)

        response = self.render_to_response(args)
        test_success = 0
        args = getpostArguments(request, test_success)
        response = self.render_to_response(args)
        response['x-frame-options'] = 'this_can_be_anything'
        return response

    def post(self, request, *args, **kwargs):
        test_success = 0
        aform = _get_form(request, submitData.SubmitResults, 'aform_pre')
        if aform.is_bound and aform.is_valid():
            plt = getPlatform(request)
            proaid = aform.cleaned_data['proa_value']
            v4dns = aform.cleaned_data['v4dns']
            v6dns = aform.cleaned_data['v6dns']
            ip_ds = aform.cleaned_data['ipds']  # change this
            ip_ds_lp = aform.cleaned_data['ipdslp']
            ipv4_nodns = aform.cleaned_data['v4nodns']
            ipv6_nodns = aform.cleaned_data['v6nodns']
            ipv6_ispdns = aform.cleaned_data['v6ispdns']
            ipv6_mtu = aform.cleaned_data['v6mtu']
            logger.debug("v4dns %s".format(v4dns))
            obj, created = IPmodel.objects.get_or_create(ipv4_dns=v4dns, ipv6_dns=v6dns,
                                                         ip_ds=ip_ds, ip_ds_lp=ip_ds_lp, ipv4_nodns=ipv4_nodns,
                                                         ipv6_nodns=ipv6_nodns, ipv6_ispdns=ipv6_ispdns, ipv6_mtu=ipv6_mtu, worker_id=proaid)

            test_success = 1
            if plt:
                test_success = 2

        args = getpostArguments(request, test_success)

        response = self.render_to_response(args)

        #response = self.render_to_response({'aform': aform, 'bform': bform,'test_success' :test_success, 'comment_success' : comment_success,})
        response['x-frame-options'] = 'this_can_be_anything'
        return response


def getpostArguments(request, test_success):
    post_args = {'aform': submitData.SubmitResults(prefix='aform_pre', initial={'v4dns': '', 'v6dns': '', 'ipds': '', 'ipdslp': '',
                                                                                'v4nodns': '', 'v6nodns': '', 'v6ispdns': '', 'v6mtu': ''}), 'success': test_success}

    if getPlatform(request) == "ProA":
        post_args['platform'] = "ProA"

    if getPlatform(request) == "MTURK":
        post_args['platform'] = "MTURK"
        post_args["assignmentId"] = request.GET.get("assignmentId", "").strip()
            post_args['AMAZON_HOST'] = "https://www.mturk.com/mturk/externalSubmit"
        post_args["worker_id"] = request.GET.get("workerId", "").strip()
        post_args["assignment_id"] = request.GET.get("assignmentId", "").strip()
        post_args["hit_id"] = request.GET.get("hitId", "").strip()
        workerid = request.GET.get("workerId", "").strip()

        if workerid:
            add_qual(workerid)

    return post_args


def getPlatform(request):

    if request.method == 'GET':
        if request.GET.get("assignmentId", ""):
            return "MTURK"
    platform = request.GET.get("platform", "")
    if platform:
        return platform
    else:
        return ""


# For production
def get_qualTypeID():
    mturk = boto3.client(service_name='mturk', region_name='us-east-1', aws_access_key_id='AWS ACCESS KEY', aws_secret_access_key='AWS SECRET KEY')
    response = mturk.list_qualification_types(
        Query='Auto',
        MustBeRequestable=True,
        MustBeOwnedByCaller=True,
    )
    return response['QualificationTypes'][0]['QualificationTypeId']


def add_qual(worker):
    mturk = boto3.client(service_name='mturk', region_name='us-east-1', aws_access_key_id='AWS ACCESS KEY', aws_secret_access_key='AWS SECRET KEY')
    qual = get_qualTypeID()
    response = mturk.associate_qualification_with_worker(
        QualificationTypeId=qual,
        WorkerId=worker,
        IntegerValue=1,
        SendNotification=False
    )

# For sandbox
# def get_qualTypeID():
#   mturk = boto3.client(service_name = 'mturk',region_name='us-east-1', endpoint_url ='https://mturk-requester-sandbox.us-east-1.amazonaws.com', aws_access_key_id='AWS ACCESS KEY', aws_secret_access_key='AWS SECRET KEY')
#   response = mturk.list_qualification_types(
#               Query='Auto',
#               MustBeRequestable=True,
#               MustBeOwnedByCaller=True,
#   )
#   return response['QualificationTypes'][0]['QualificationTypeId']
