# Python SDK Bulk Event Dispatcher  

This is a reference implementation of a bulk event dispatcher for the Optimizely [Full Stack Python SDK](https://github.com/optimizely/python-sdk). The dispatcher defines how events are sent to Optimizely for analytics tracking. Read more in the event dispatcher [documentation](https://developers.optimizely.com/x/solutions/sdks/reference/?language=python#event-dispatcher).  

By default, the dispatcher is synchronous and dispatches on a per event basis via separate HTTP calls to Optimizely’s logging endpoint. This implementation batches events and sends in bulk by leveraging a producer/consumer model.

The producer is responsible for writing events to [AWS SQS](https://aws.amazon.com/sqs/) so they can be maintained in a queue. The consumer then runs on [AWS Lambda](https://aws.amazon.com/lambda/) at a set interval to flush the queue. This process aggregates the events and makes a single request to Optimizely. 

## Architecture 

<img src="https://s3-us-west-2.amazonaws.com/mauerbac-static-images/diagram.png" alt="diagram" width="516.75" height="294.75"/>

# Getting Started 

To get started, you will need to setup the consumer and producer using `event_dispatcher.py` and `lambda_function.py`, as well as configure the AWS environment and create a Optimizely Python project. If this is your first Optimizely project, check out the [getting started guide](https://developers.optimizely.com/x/solutions/sdks/getting-started/index.html?language=python).  

## Producer

__SQS__

1. In AWS, create a new queue called `event-queue`. Use a standard queue.
2. Configure the settings as needed. I recommend a visibility timeout of `1 min` & receive message wait time of `20 secs`. 

__Python SDK__

1. This dispatcher should be added to the Python SDK and [passed in](https://developers.optimizely.com/x/solutions/sdks/reference/?language=python#event-dispatcher) as follows:

```
from .event_dispatcher_bulk import EventDispatcher as event_dispatcher

// Create an Optimizely client with the default event dispatcher
optimizely_client = optimizely.Optimizely(datafile,
                                          event_dispatcher=event_dispatcher)
```

2. Provide the Python SDK with your AWS credentials. Ideally, use environment variables: `AWS_KEY` & `AWS_SECRET`. Note: I’ve set the region to `us-west-2`.  

3. Rebuild & install the SDK. Instructions in the Python SDK [readme](https://github.com/optimizely/python-sdk/blob/master/README.md).

## Consumer

__Lambda__

1. In `lamdba_function.py` provide your Optimizely account_id & project_id. This can be found in your datafile.
2. Create a new lambda function via the blank function template.
3. Add CloudWatch Events as the configured trigger.
4. Create a new rule with a scheduled expression depending on your desired frequency. Ie. `rate(1 minute)` to flush the queue every minute. [Syntax](http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)
5. Give the function a name, description and runtime `Python 2.7`
6. Provide a AWS role policy that provides full access to SQS
7. Upload the function (`lambda_function.py`) as well as the necessary dependencies via a .ZIP file. 
8. Under advanced settings, set the timeout to 1 minute. Depending on the workload, you might need to increase this.
9. Create the function!


