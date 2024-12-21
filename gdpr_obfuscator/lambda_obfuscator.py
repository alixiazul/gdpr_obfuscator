import json
import boto3
from obfuscator import Obfuscator

def lambda_handler(event, context):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']

        s3 = boto3.client('s3')     
   
        json_string = f'{{"file_to_obfuscate": "s3://{bucket_name}/{file_key}"}}'
        obfuscator = Obfuscator(json_string)
        obfuscated_file = obfuscator.obfuscate()
        
        response = s3.put_object(Bucket=bucket_name, Key=file_key, Body=obfuscated_file.getvalue().encode('utf-8'))
        
        return {
            'statusCode': 200,
            'body': response
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }