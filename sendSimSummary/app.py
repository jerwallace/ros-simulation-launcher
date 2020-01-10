import json
import boto3

pipeline = boto3.client('codepipeline')

def lambda_handler(event, context):
    
    output = {
        "message": "No results.",
        "results": []
    }
    
    output["results"].extend(event['results'])
    
    for job_output in event['results']:
        
        if (job_output['status']=='Failed'):
            output["message"] = "There was an error in the execution of one or more of your simulations."
            code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
                'type': 'JobFailed',
                'message': output["message"]
            })
            return output
            
        else:
            for key in job_output['tags'].keys():
                if job_output['tags'][key] == "Failed":
                    output["message"] = "One or more tests failed in simulation."
                    code_pipeline_response = pipeline.put_job_failure_result(jobId=event['codePipelineJobId'], failureDetails={
                        'type': 'JobFailed',
                        'message': output["message"]
                    })
                    return output
                    
        output["message"] =  "%i simulations successfully passed tests." % len(event['results'])
        code_pipeline_response = pipeline.put_job_success_result(jobId=event['codePipelineJobId'], executionDetails={'summary': json.dumps(output)})
        
    return output
