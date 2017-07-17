# Copyright 2016, Optimizely
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import requests
import boto3
import os

from requests import exceptions as request_exception

from .helpers import enums

REQUEST_TIMEOUT = 10


def connect_to_sqs():
  sqs = boto3.resource('sqs',
    aws_access_key_id=os.environ['AWS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET'], 
    region_name='us-west-2')
  return sqs.get_queue_by_name(QueueName='event-queue')

class EventDispatcher(object):

  @staticmethod
  def dispatch_event(event):
    """ Dispatch the event being represented by the Event object.

    Args:
      event: Object holding information about the request to be dispatched to AWS SQS
    """
    # TO DO need to keep connection to sqs open
    # use async lib to enqueue in another thread
    queue = connect_to_sqs() 
    logging.info('Writing event to SQS:' + str(json.dumps(event.params)))

    visitor = event.params['visitors'][0]['visitor_id']
    attributes = event.params['visitors'][0]['attributes']
    snapshot = event.params['visitors'][0]['snapshots'][0]

    response = queue.send_message(MessageBody=json.dumps({visitor: (attributes, snapshot)}))

