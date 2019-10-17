
import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import re
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
lambda_client = boto3.client('lambda')


regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    # print ("Session :", session_attributes)
    # invoke_response = lambda_client.invoke(FunctionName="LF2",InvocationType='RequestResponse')
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None

def isvaild_num_people(num_people):
    if safe_int(num_people) > 0:
        return True
    return False
        
def isvalid_cuisine(cuisine):
    valid_cuisine = ['indian', 'chinese', 'american', 'italian', 'japanese', 'mexican', 'spanish']
    return cuisine.lower() in valid_cuisine

def isvalid_phone_num(phone_num):
    if len(phone_num) == 10:
        return True
    return False
        

def isvalid_city(city):
    valid_cities = ['new york']
    return city.lower() in valid_cities


def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False

def isvalid_time(dine_time, dining_date):
    if datetime.datetime.strptime(dining_date, '%Y-%m-%d').date() == datetime.date.today():
        now = datetime.datetime.now()
        hour = datetime.datetime.strptime(dine_time, '%H:%M').time().hour
        min = datetime.datetime.strptime(dine_time, '%H:%M').time().minute
        dining_time = now.replace(hour=hour, minute=min, second=0, microsecond=0)
        if now >= dining_time:
            return False
    return True

def isvalid_email(email):  
    if(re.search(regex,email)):  
        return True  
          
    else:  
        return False

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }

def validate_book_restaurant(slots):
    location = try_ex(lambda: slots['Location'])
    num_people = try_ex(lambda: slots['NumberOfPeople'])
    cuisine = try_ex(lambda: slots['Cuisine'])
    dining_date = try_ex(lambda: slots['DiningDate'])
    dining_time = try_ex(lambda: slots['Time'])
    # phone_num = try_ex(lambda: slots['PhoneNumber'])
    email = try_ex(lambda: slots['Email'])
    
    if location and not isvalid_city(location):
        return build_validation_result(
            False,
            'Location',
            'We are still expanding our horizon. Sorry for the inconvenience but you might want to try a different city.')
            
    
    if num_people and not isvaild_num_people(num_people):
        return build_validation_result(
            False,
            'NumberOfPeople',
            'I don\'t think people should be negative. Please try to be positive!')

    
    if cuisine and not isvalid_cuisine(cuisine):
        return build_validation_result(
            False,
            'Cuisine',
            'Sorry, I don\'t know much about this cuisine. Lets try something else!')
            
    # if phone_num and not isvalid_phone_num(phone_num):
    #     return build_validation_result(False, 'PhoneNumber', 'Please give me a valid phone number of yours, so that I can notify you about your booking!')
        
    if email and not isvalid_email(email):
        return build_validation_result(False, 'Email', 'Please give me a valid email id of yours, so that I can notify you about your booking!')

    if dining_date:
        if not isvalid_date(dining_date):
            return build_validation_result(False, 'DiningDate', 'I did not understand your dining date.  When would you like to dine?')
        if datetime.datetime.strptime(dining_date, '%Y-%m-%d').date() < datetime.date.today():
            return build_validation_result(False, 'DiningDate', 'Reservations must be scheduled at least one day in advance.  Can you try a different date?')
            
    if dining_time and not isvalid_time(dining_time, dining_date):
            return build_validation_result(False, 'Time', 'Not a valid time. What time would you like to dine?')
        
    return {'isValid': True}


""" --- Functions that control the bot's behavior --- """

def book_restaurant(intent_request):
    location = try_ex(lambda: intent_request['currentIntent']['slots']['Location'])
    num_people = try_ex(lambda: intent_request['currentIntent']['slots']['NumberOfPeople'])
    cuisine = try_ex(lambda: intent_request['currentIntent']['slots']['Cuisine'])
    dining_date = try_ex(lambda: intent_request['currentIntent']['slots']['DiningDate'])
    dining_time = try_ex(lambda: intent_request['currentIntent']['slots']['Time'])
    # phone_num = try_ex(lambda: intent_request['currentIntent']['slots']['PhoneNumber'])
    email = try_ex(lambda: intent_request['currentIntent']['slots']['Email'])
    
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    
    # to confirm
    restaurant_req = json.dumps({
        'Location': location,
        'NumberOfPeople': num_people,
        'Cuisine': cuisine,
        'DiningDate': dining_date,
        'Time': dining_time,
        # 'PhoneNumber': phone_num,
        'Email': email
    })

    session_attributes['currentRestaurantReq'] = restaurant_req
    
    # to confirm
    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_book_restaurant(intent_request['currentIntent']['slots'])
        if not validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )
            
        return delegate(session_attributes, intent_request['currentIntent']['slots'])
    # logger.debug('bookHotel under={}'.format(reservation))
    
    # Here upon fulfillment push the slots in sqs queue and trigger LF2 for restaurant suggestions
    print ("Session attributes", json.loads(session_attributes['currentRestaurantReq']))
    restaurantSQSRequest(json.loads(session_attributes['currentRestaurantReq']))
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks, for the details. Hold on, reccommending you some good restaurants! '
        }
    )

    #sending messages from sqs to LF1
    
def restaurantSQSRequest(requestData):
    sqs = boto3.client('sqs')
    queue_url = 'https://sqs.us-east-1.amazonaws.com/777754410071/SQS_Q1_Test'
    delaySeconds = 5
    messageAttributes = {
       'Location': {
            'DataType': 'String',
            'StringValue': requestData['Location']
        },
       'NumberOfPeople': {
            'DataType': 'Number',
            'StringValue': requestData['NumberOfPeople']
        },
        # 'PhoneNumber': {
        #     'DataType': 'Number',
        #     'StringValue': requestData['PhoneNumber']
        # },
        'Cuisine':{
            'DataType':'String',
            'StringValue': requestData['Cuisine']
        },
        'DiningDate': {
            'DataType':'String',
            'StringValue': requestData['DiningDate']
        },
        'Time': {
            'DataType':'String',
            'StringValue': requestData['Time']
        },
        'Email': {
            'DataType':'String',
            'StringValue': requestData['Email']
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
    print("Response : ", response)
    # print(response['MessageId'])
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

# --- Intents ---


def dispatch(intent_request):
    print (intent_request)
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'DiningSuggestionsIntent':
        return book_restaurant(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
