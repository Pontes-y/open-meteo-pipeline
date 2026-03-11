#!/bin/bash

# Create deployment package for AWS Lambda
rm -rf lambda_package.zip
cd lambda_package
pip install -r requirements.txt --target .
zip -r ../lambda_package.zip . -x "*.pyc" -x "__pycache__/"
cd ..
echo "Deployment package created: lambda_package.zip"