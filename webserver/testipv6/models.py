from django.core.validators import URLValidator
from django.db import models
import re
import django
from unixtimestampfield.fields import UnixTimeStampField


# Create your models here.

class IPAddresses(models.Model):

    ipv4_dns = models.GenericIPAddressField()
    ipv6_dns = models.GenericIPAddressField(protocol='IPv6')
    ip_ds = models.GenericIPAddressField(protocol='both')  # change this
    ip_ds_lp = models.GenericIPAddressField(protocol='both')
    ipv4_nodns = models.GenericIPAddressField()
    ipv6_nodns = models.GenericIPAddressField(protocol='IPv6')
    date = UnixTimeStampField(auto_now_add=True)


class AmazonResults(models.Model):
    user = models.ForeignKey(IPAddresses)
    worker_id = models.CharField(max_length=50, default='')
    assignment_id = models.CharField(max_length=50, default='')
    hit_id = models.CharField(max_length=50, default='')
    accepted = models.BooleanField(default=False)
    url = models.URLField(default='')


class ProA(models.Model):
    pro_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(IPAddresses)
    worker_id = models.CharField(max_length=50, default='')

    class Meta:
        unique_together = ('pro_id', 'user')
