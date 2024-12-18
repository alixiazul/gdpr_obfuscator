import json
import boto3
from io import StringIO
from obfuscator import Obfuscator

def lambda_handler(event, context):
    try:
        # Extract the S3 bucket name and the file key from the event
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']

        # print("Bucket name: ", bucket_name)
        # print("File key: ", file_key)

        # Initialize an S3 client using Boto3
        s3 = boto3.client('s3')
        
        # Fetch the file from the S3 bucket
        # file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        # file_content = file_obj['Body'].read().decode('utf-8')  # Read the file content as a string
        # print("File content: ", file_content)
        
        json_string = f'{{"file_to_obfuscate": "s3://{bucket_name}/{file_key}"}}'

        obfuscator = Obfuscator(json_string)
        obfuscated_file = obfuscator.obfuscate()
        # print("Obfuscated_file: ", obfuscated_file)
        
        # key_parts = file_key.split('/')
        # file_name = key_parts[-1]  # Extract the file name
        # obfuscated_file_name = f"obfuscated_{file_name}"  # Add the prefix

        # output_key = '/'.join(key_parts[:-1] + [obfuscated_file_name])  # Reconstruct the path with the new file name
        output_key = file_key
        
        # Upload the obfuscated file back to the same S3 bucket
        #s3.put_object(Bucket=bucket_name, Key=output_key, Body=obfuscated_file)
        response = s3.put_object(Bucket=bucket_name, Key=output_key, Body=obfuscated_file.getvalue().encode('utf-8'))
        
        # Return a success response
        return {
            'statusCode': 200,
            'body': response
        }
    
    except Exception as e:
        # If there's an error, return an error message
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }