import json
import boto3

pipeline = boto3.client('codepipeline')
        
def lambda_handler(event, context):
    code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
            'type': 'JobFailed',
            'message': event['error']['Cause']
    })
        
    return "Simulations failed."