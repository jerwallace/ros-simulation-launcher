import json
import boto3

client = boto3.client('robomaker')

def lambda_handler(event, context):

    output = { "isDone": False }
    
    if (event["arn"]):  
        response = client.describe_simulation_job(
            job=event["arn"]
        )
        output["tags"] = response["tags"]
        output["arn"] = response["arn"]
        output["status"] = response["status"]
        
        if (response["status"] == "Failed" or response["status"] == "Completed" or response["status"] == "Canceled"):
            output["isDone"] = True
        else:
            output["isDone"] = False
            
    else:
        output["isDone"] = True
        output["status"] = "Failed"

    return output