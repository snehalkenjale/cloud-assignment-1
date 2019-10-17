import boto3
import requests
import json
from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource('dynamodb')

tableName = "yelp_restaurants_1"
table = dynamodb.Table(tableName)

region = 'us-east-1'
service = 'es'
host = 'https://search-yelp-restaurants-domain-fisoghxvlz63b5skhjjsiixg4m.us-east-1.es.amazonaws.com'

index = 'restaurants'
type = 'Restaurant'

url = host + '/' + index + '/_search?'

headers = headers = {'Content-Type': "application/json"}

cuisine = "indian"

search_params = """{"query":{"bool":{"must":[{"match":{"cuisine":\"""" + cuisine + """\"}}],"must_not":[],"should":[]}},"from":0,"size":3,"sort":[],"aggs":{}}"""


def get_data(event=None, context=None):
    
    response = requests.get(url=url, data=search_params, headers=headers)
    dict1 = json.loads(response.text)
    records = []
    for i in dict1.get("hits").get("hits"):
        x = table.query(KeyConditionExpression=Key('id').eq(i.get("_id")))
        records.append(x)
	return records
    
        


