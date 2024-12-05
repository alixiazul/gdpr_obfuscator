import json
import boto3
from io import StringIO
from obfuscator import Obfuscator

def lambda_handler(event, context):
    try:
        # Extract the S3 bucket name and the file key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        
        # Initialize an S3 client using Boto3
        s3 = boto3.client('s3')
        
        # Fetch the file from the S3 bucket
        file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = file_obj['Body'].read().decode('utf-8')  # Read the file content as a string
        
        
        obfuscator = Obfuscator()
        obfuscated_file = obfuscator.obfuscate(file_content)        
        
        key_parts = file_key.split('/')
        file_name = key_parts[-1]  # Extract the file name
        obfuscated_file_name = f"obfuscated_{file_name}"  # Add the prefix

        output_key = '/'.join(key_parts[:-1] + [obfuscated_file_name])  # Reconstruct the path with the new file name

        
        # Upload the obfuscated file back to the same S3 bucket
        s3.put_object(Bucket=bucket_name, Key=output_key, Body=obfuscated_file)
        
        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps(f"Obfuscated file saved to s3://{bucket_name}/{output_key}")
        }
    
    except Exception as e:
        # If there's an error, return an error message
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }