import json
import boto3
# import requests
client = boto3.client('robomaker')
        
def lambda_handler(event, context):

    response = client.create_simulation_job(**event)

    if (response):
        output = { "arn": response["arn"] }
        
    return output