import boto3
import os
import time

def restaurantSQSRequest(requestData):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/777754410071/SQS_Q1_Test'
    delaySeconds = 5
    messageAttributes = {
       'Location': {
            'DataType': 'String',
            'StringValue': requestData['location']
        },
       'NumberOfPeople': {
            'DataType': 'Number',
            'StringValue': requestData['num_people']
        },
        'PhoneNumber': {
            'DataType': 'Number',
            'StringValue': requestData['phone_num']
        },
        'Cuisine':{
            'DataType':'String',
            'StringValue': requestData['cuisine']
        },
        'DiningDate': {
            'DataType':'String',
            'StringValue': requestData['dining_time']
        },
        'Email': {
            'DataType': 'String',
            'StringValue': requestData['email']
        }
        'Time': {
            'DataType': 'String',
            'StringValue': requestData['time']
        }

    }
    messageBody=('Recommendation for the food')
    
    response = sqs.send_message(
        QueueUrl = queue_url,
        DelaySeconds = delaySeconds,
        MessageAttributes = messageAttributes,
        MessageBody = messageBody
        )
    
    print ('send data to queue')
    print(response)
    
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    #logger.debug('event.bot.name={}'.format(event['bot']['name']))
    restaurantSQSRequest(event)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }