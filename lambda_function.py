# PYTHON 2.7 ONLY
import boto3
import json
import requests


def lambda_handler(event, context):

  project_id = 'xxxxxxx' # Provide project_id

  sqs = boto3.resource('sqs',region_name='us-west-2')
  queue = sqs.get_queue_by_name(QueueName='event-queue')

  # Option 1: Use datafile to provide account_id 
  #url = 'https://cdn.optimizely.com/json/{}.json'.format(project_id)
  #datafile = requests.get(url).text
  #config = json.loads(datafile)
  #account_id = config.get('accountId')
  
  # Option 2: Hard code project/account ID 
  account_id = 'xxxxxxxx'  # Provide account_id
  client_name = 'python-sdk'
  client_version = '1.2.0'

  obj = {
    'account_id': account_id,
    'client_name': client_name,
    'client_version': client_version,
    'project_id': project_id,
    'visitors': [] 
  }

  items_temp = []
  user_map = {}
  attributes_map = {}

  # Poll SQS -- with few events you must poll sqs multiple times. items_temp is used to ensure we have all events
  for x in range(0, 5):
    items = queue.receive_messages(WaitTimeSeconds=1, MaxNumberOfMessages=10)
    items_temp.extend(items)

  # Build a mapping of visitors to snapshot and visitors to attributes 
  for item in items_temp:
    decode_item = json.loads(item.body)
    key = decode_item.keys()[0]
    attributes = decode_item[key][0]
    snapshot = decode_item[key][1]
    if key in user_map:
      user_map[key].append(snapshot)
    else:
      user_map[key] = [snapshot]
      attributes_map[key] = attributes
    item.delete()

  # Build single request objet
  for visitor in user_map:
    entry = {
      'visitor_id': visitor,
      'attributes': attributes_map[visitor],
      'snapshots': user_map[visitor]
    }
    obj['visitors'].append(entry)

  # send object
  requests.post('https://logx.optimizely.com/v1/events', data=json.dumps(obj), headers={'Content-Type': 'application/json'})

  return True