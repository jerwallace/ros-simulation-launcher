import json
import boto3
import time

pipeline = boto3.client('codepipeline')
client = boto3.client('robomaker')

def lambda_handler(event, context):
    
    output = {
        "message": "No results.",
        "codePipelineJobId": event['codePipelineJobId'],
        "batchSimJobArn": event["batchSimJobArn"]
    }
        
    response = client.describe_simulation_job_batch(
        batch = event["batchSimJobArn"]
    )
    
    print(response)

    if event["status"] == "Success" and len(response['failedRequests']) == 0:
        
        for job_output in response['createdRequests']:
            
            job_response = client.describe_simulation_job(
                job=job_output["arn"]
            )
            
            for key in job_response['tags'].keys():
                if job_response['tags'][key] == "Failed":
                    output["message"] = "One or more tests failed in simulation."
                    code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
                        'type': 'JobFailed',
                        'message': output["message"]
                    })
                    return output
                    
            time.sleep(1)
    else:
        output["message"] = "There was an error in the execution of one or more of your simulations."
        code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
            'type': 'JobFailed',
            'message': output["message"]
        })
        return output
    
    output["message"] =  "%i simulations successfully passed tests." % len(response['createdRequests'])
    code_pipeline_response = pipeline.put_job_success_result(jobId=event['codePipelineJobId'], executionDetails={'summary': json.dumps(output)})

    return output