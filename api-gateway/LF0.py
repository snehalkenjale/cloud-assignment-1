import json
import boto3

client = boto3.client('lex-runtime')

def lambda_handler(event, context):
    
    lastUserMessage = event['message'];
    botMessage = "There is something wrong, Please start process once again.";
    
    if lastUserMessage is None or len(lastUserMessage) < 1:
        return {
            'statusCode': 200,
            'body': json.dumps(botMessage)
        }
    
    # Update the user id, so it is different for different user
    response = client.post_text(botName='FoodieBot',
        botAlias='chatbotFoodie',
        userId='USER1',
        inputText=lastUserMessage)
    
    if response['message'] is not None or len(response['message']) > 0:
        lastUserMessage = response['message']
    
    
    return {
        'statusCode': 200,
        'body': json.dumps(lastUserMessage)
    }