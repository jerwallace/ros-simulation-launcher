import json
import boto3
import time

pipeline = boto3.client('codepipeline')
client = boto3.client('robomaker')

def lambda_handler(event, context):
    
    output = {
        'message': 'No results.',
        'codePipelineJobId': event['codePipelineJobId'],
        'batchSimJobArn': event['batchSimJobArn']
    }

    if event['status'] == 'Success':
        job_response = client.batch_describe_simulation_job( jobs = event['arns'] )
        for job in job_response:
            for key in job['tags'].keys():
                if job_response['tags'][key] == 'Failed':
                    output['message'] = 'One or more tests failed in simulation.'
                    code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
                        'type': 'JobFailed',
                        'message': output['message']
                    })
                    return output
                    
    else:
        output['message'] = 'There was an error in the execution of one or more of your simulations.'
        code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
            'type': 'JobFailed',
            'message': output['message']
        })
        return output
    
    output['message'] =  '%i simulations successfully passed tests.' % len(event['arns'])
    code_pipeline_response = pipeline.put_job_success_result(jobId=event['codePipelineJobId'], executionDetails={'summary': json.dumps(output)})

    return output