# PYTHON 2.7 ONLY
import boto3
import json
import requests


def lambda_handler(event, context):

  project_id = '8449080257' # required field

  sqs = boto3.resource('sqs',region_name='us-west-2')
  queue = sqs.get_queue_by_name(QueueName='event-queue')
  
  # get base level events 1) use datafile 2) look at a single event ?
  # create base object
  # get basic info
  url = 'https://cdn.optimizely.com/json/{}.json'.format(project_id)
  datafile = requests.get(url).text
  config = json.loads(datafile)

  account_id = config.get('accountId')
  client_name = 'python-sdk'
  client_version = '1.2.0'

  obj = {
    'account_id': account_id,
    'client_name': client_name,
    'client_version': client_version,
    'project_id': project_id,
    'visitors': [] 
  }

  items_hold = []
  user_map = {}
  attributes_map = {}

  for x in range(0, 5):
    items = queue.receive_messages(WaitTimeSeconds=1, MaxNumberOfMessages=10)
    items_hold.extend(items)

  # to do : check items exist in here
  # build map dict
  for item in items_hold:
    decode_item = json.loads(item.body)
    key = decode_item.keys()[0]
    attributes = decode_item[key][0]
    snapshot = decode_item[key][1]
    if key in user_map:
      user_map[key].append(snapshot)
    else:
      user_map[key] = [snapshot]
      # also store attributes
      attributes_map[key] = attributes
    item.delete()

  for visitor in user_map:
    entry = {
      'visitor_id': visitor,
      'attributes': attributes_map[visitor],
      'snapshots': user_map[visitor]
    }
    obj['visitors'].append(entry)

  print("batch event object ", obj)
  # send object
  requests.post('https://logx.optimizely.com/v1/events', data=json.dumps(obj), headers={'Content-Type': 'application/json'})


  return True