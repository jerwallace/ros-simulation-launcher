import json
import boto3

client = boto3.client('robomaker')

def lambda_handler(event, context):
    
    if (event["batchSimJobArn"]):  
        
        output = { "isDone": False, "batchSimJobArn": event["batchSimJobArn"], "status": "Success", "codePipelineJobId": event["codePipelineJobId"]}
        
        response = client.describe_simulation_job_batch(
            batch = event["batchSimJobArn"]
        )
        
        if response['status'] == 'Completed':
            output["isDone"] = True
            output["status"] = "Success"
        elif response['status'] == 'Failed' or response['status'] == 'Canceled':
            output["isDone"] = True
            output["status"] = "Failed"
            
    else:
        output["isDone"] = True
        output["status"] = "Failed"

    return output