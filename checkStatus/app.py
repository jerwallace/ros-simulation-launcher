import json
import boto3

client = boto3.client('robomaker')

def lambda_handler(event, context):
    
    if (event['batchSimJobArn']):  
        
        output = { 'arns': [], 'isDone': False, 'batchSimJobArn': event['batchSimJobArn'], 'status': 'Success', 'codePipelineJobId': event['codePipelineJobId']}
        
        response = client.describe_simulation_job_batch(
            batch = event['batchSimJobArn']
        )
        
        if response['status'] == 'Completed':
            output['isDone'] = True
            
            if len(response['failedRequests']) == 0:
                output['status'] = 'Success'
            else:
                output['status'] = 'Failed'
                
            for job_output in response['createdRequests']:
                output['arns'].append(job_output['arn'])
            
        elif response['status'] == 'Failed' or response['status'] == 'Canceled':
            output['isDone'] = True
            output['status'] = 'Failed'
 
    else:
        output['isDone'] = True
        output['status'] = 'Failed'

    return output