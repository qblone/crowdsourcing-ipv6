""""" 
__author Qasim 

This files read new and old files and find the new records
It then checks the links and update databases for valid entries 

"""
import csv


import csv
import difflib
import sqlite3
import ipaddress
from lxml import html
import requests
from datetime import datetime
from pytz import timezone
import pytz
import math
utc = pytz.utc
from pprint import pprint
import boto3
import xml.etree.ElementTree as ET


class UpDataDB():

  def getEpochTime(self, dt):
    p = '%c'
    dt_new = dt.split()
    local_dt = '{0} {1} {2} {3} {4}'.format(dt_new[0], dt_new[1], dt_new[2], dt_new[3], dt_new[5])
    epoch = datetime(1970, 1, 1)
    tm_tz = datetime.strptime(local_dt, p)
    tz = pytz.timezone('America/New_York')
    eastern = timezone('US/Eastern')
    edt = eastern.localize(tm_tz, is_dst=True)
    utc_dt = edt.astimezone(utc)
    fmt = '%Y-%m-%d %H:%M:%S'
    utc_str = utc_dt.strftime(fmt)
    dt1 = datetime.strptime(utc_str, fmt)
    epoch_time = (dt1 - epoch).total_seconds()
    print(epoch_time)
    print(dt)
    return epoch_time

  def getEpochTime_from_dt(self, dt):
    epoch = datetime(1970, 1, 1)
    tz = pytz.timezone('America/New_York')
    #eastern = timezone('US/Eastern')
    #edt = eastern.localize(dt, is_dst=True)
    utc_dt = dt.astimezone(utc)
    fmt = '%Y-%m-%d %H:%M:%S'
    utc_str = utc_dt.strftime(fmt)
    dt1 = datetime.strptime(utc_str, fmt)
    epoch_time = (dt1 - epoch).total_seconds()
    return epoch_time

  def createAmazonUser(self, worker_id, assignmentId, hit_id):
    conn = sqlite3.connect("/home/code/ipv6/db.sqlite3")
    cursor = conn.cursor()
    sql = '''Insert into testipv6_amazonresults
        (worker_id,assignment_id,hit_id)
        values (?,?,?) '''
    print(sql, worker_id, 1, assignmentId, hit_id)
    cursor.execute(sql, (worker_id, assignmentId, hit_id))
    cursor.close()
    conn.commit()
    conn.close()
    print("Updated table")

  def addToCompletedTests(self, worker_id, ipv4_dns, ipv6_dns, ip_ds, ip_ds_lp, ipv6_mtu, ipv6_ispdns, dt):
    conn = sqlite3.connect("/home/code/ipv6/db.sqlite3")
    cursor = conn.cursor()
    sql = """ INSERT into testipv6_ipaddresses  (worker_id,ipv4_dns,ipv6_dns,ip_ds,ip_ds_lp,ipv6_mtu,ipv6_ispdns,date) values (?,?,?,?,?,?,?,?) """
    cursor = conn.cursor()
    cursor.execute(sql, (worker_id, ipv4_dns, ipv6_dns, ip_ds, ip_ds_lp, ipv6_mtu, ipv6_ispdns, dt))
    cursor.close()
    conn.commit()
    conn.close()

    print("Added value to completed tests!")

  def update_from_platform(self, hit_id, workerid):
    #mturk = boto3.client(service_name = 'mturk',endpoint_url ='https://mturk-requester-sandbox.us-east-1.amazonaws.com')
    mturk = boto3.client(service_name='mturk', region_name='us-east-1')
    response = mturk.list_assignments_for_hit(
        HITId=hit_id,
        AssignmentStatuses=['Submitted'],
    )
    assignments = response['Assignments']
    for assignment in assignments:
      worker_id = assignment['WorkerId']
      assignmentId = assignment['AssignmentId']
      answer = assignment['Answer']
      submitTime = assignment['SubmitTime']
      print(type(submitTime))
      epoch = datetime.utcfromtimestamp(0)
      dt = self.getEpochTime_from_dt(submitTime)
      print(dt)
      print(submitTime)
      # raise()
      #print ('The Worker with ID {} submitted assignment {} and gave the answer {}'.format(WorkerId,assignmentId,answer))
      tree = ET.ElementTree(ET.fromstring(answer))
      ns = {'ns': 'http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionFormAnswers.xsd'}
      attr_values = dict()
      for res in tree.findall('ns:Answer', ns):
        attr = res.find('ns:QuestionIdentifier', ns).text
        val = res.find('ns:FreeText', ns).text
        attr_values[attr] = val
        print(attr, val)
      print(attr_values)

      ipv4_dns, ipv6_dns, ip_ds, ip_ds_lp, ipv6_ispdns, worker_id, ipv6_mtu = '', '', '', '', '', '', ''

      if 'aform_pre-v4dns' in attr_values:
        ipv4_dns = attr_values['aform_pre-v4dns']
      if 'aform_pre-v6dns' in attr_values:
        ipv6_dns = attr_values['aform_pre-v6dns']
      if 'aform_pre-ipds' in attr_values:
        ip_ds = attr_values['aform_pre-ipds']
      if 'aform_pre-ipdslp' in attr_values:
        ip_ds_lp = attr_values['aform_pre-ipdslp']
      if 'aform_pre-v6mtu' in attr_values:
        ipv6_mtu = attr_values['aform_pre-v6mtu']
      if 'aform_pre-v6nodns' in attr_values:
        ipv6_ispdns = attr_values['aform_pre-v6nodns']
      if 'workerId' in attr_values:
        worker_id = attr_values['workerId']

      self.createAmazonUser(worker_id, assignmentId, hit_id)
      self.addToCompletedTests(worker_id, ipv4_dns, ipv6_dns, ip_ds, ip_ds_lp, ipv6_mtu, ipv6_ispdns, dt)
