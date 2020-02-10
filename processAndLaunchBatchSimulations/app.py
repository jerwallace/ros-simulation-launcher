
'''
    In this sample lambda function, multiple simulation jobs will be run based on a common configuration.
    
    Below is a sample event that you could use to invoke the lambda function and launch a set of simulations.
    
    {
        "scenarios": {
            "": {
                "robotEnvironmentVariables": {}
                "simEnvironmentVariables": {}
            }
        },
        "simulations": [{
            "scenarios": ["<SCENARIO_NAME>"]
            "params": CreateSimulationJobParams
        }]
    }
    
'''

import json
import time
import uuid
import os
import boto3
from copy import deepcopy

client = boto3.client('robomaker')

def lambda_handler(event, context):
    
    output = {
        'isValid': True,
        'isDone': False,
        'codePipelineJobId': event['codePipelineJobId'],
        'batchSimJobArn': None,
        'createdRequests': None
    }
    
    jobs = []
    
    for simulation in event['simulations']:
            
        print("Preparing simulation %s..." % json.dumps(simulation))
        
        if "S3_BUCKET" in os.environ and not simulation['params']['outputLocation']['s3Bucket'].strip():
            simulation['params']['outputLocation']['s3Bucket'] = os.getenv("S3_BUCKET")
 
        if "IAM_ROLE" in os.environ and not simulation['params']['iamRole'].strip():
            simulation['params']['iamRole'] = os.getenv("IAM_ROLE")
                    
        if simulation['params']['vpcConfig']:
            if "SECURITY_GROUP" in os.environ and os.getenv("SECURITY_GROUP") not in simulation['params']['vpcConfig']['securityGroups']:
                simulation['params']['vpcConfig']['securityGroups'].append(os.getenv("SECURITY_GROUP"))
            if "SUBNET_1" in os.environ and os.getenv("SUBNET_1") not in simulation['params']['vpcConfig']['subnets']:
                simulation['params']['vpcConfig']['subnets'].append(os.getenv("SUBNET_1"))
            if "SUBNET_2" in os.environ and os.getenv("SUBNET_2") not in simulation['params']['vpcConfig']['subnets']:
                simulation['params']['vpcConfig']['subnets'].append(os.getenv("SUBNET_2"))
        
        for x, scenario in enumerate(simulation['scenarios']):
            
            if scenario in event['scenarios'].keys():
                
                _sim_params = deepcopy(simulation['params'])
                
                print("Scenario %s found..." % scenario)
        
                _sim_params['tags'] = { "Scenario": scenario }
                y, z = 0, 0
        
                for y, robotApp in enumerate(_sim_params['robotApplications']):
                    _sim_params['robotApplications'][y]['launchConfig']['environmentVariables'] = event['scenarios'][scenario]['robotEnvironmentVariables']
                    if "ROBOT_APP_ARN" in os.environ and not _sim_params['robotApplications'][y]['application'].strip():
                        _sim_params['robotApplications'][y]['application'] = os.getenv("ROBOT_APP_ARN")
                    
                for z, simApp in enumerate(_sim_params['simulationApplications']):
                    _sim_params['simulationApplications'][z]['launchConfig']['environmentVariables'] = event['scenarios'][scenario]['simEnvironmentVariables']
                    if "SIMULATION_APP_ARN" in os.environ and not _sim_params['simulationApplications'][z]['application'].strip():
                        _sim_params['simulationApplications'][z]['application'] = os.getenv("SIMULATION_APP_ARN")
                
                print("Adding following job: " + json.dumps(_sim_params))
                
                jobs.append(_sim_params)
                
            else:
                output['isValid'] = False
                output['error'] = {
                    "Cause": "Scenario not defined."
                }
                
        response = client.start_simulation_job_batch(
        batchPolicy={
            'timeoutInSeconds': 800,
            'maxConcurrency': 2
        }, 
        createSimulationJobRequests=jobs, 
        tags = {
             'launcher': 'cicd_pipeline',
             'codePipelineJobId': event['codePipelineJobId']
        })
        
        output['batchSimJobArn'] = response['arn']
        output['createdRequests'] = response['createdRequests']
        
    return output