#!/bin/bash
sam build --use-container
sam package --template-file template.yml --output-template-file package.yml --s3-bucket <YOUR_BUCKET>
sam deploy --template-file package.yml --stack-name cicd --capabilities CAPABILITY_NAMED_IAM