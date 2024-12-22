import json
import boto3
import logging
from obfuscator import Obfuscator

def lambda_handler(event, context):

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    pii_fields = []

    if "Records" in event:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        file_key = event['Records'][0]['s3']['object']['key']
        file_to_obfuscate = f"s3://{bucket_name}/{file_key}"
        pii_fields = ["name", "email_address"]
    else:
        file_to_obfuscate = event.get('file_to_obfuscate')
        pii_fields = event.get('pii_fields')
        bucket_name, file_key = file_to_obfuscate.replace("s3://", "").split("/", 1)

    if not file_to_obfuscate:
        return {
            'statusCode': 500,
            'body': 'file_to_obfuscate is missing'
        }
    
    json_string = json.dumps({"file_to_obfuscate": file_to_obfuscate, "pii_fields": pii_fields})
    obfuscator = Obfuscator(json_string)

    try:
        obfuscated_file = obfuscator.obfuscate()
    except ValueError as ve:
        return {
            'statusCode': 400,
            'body': json.dumps(f"ValueError: {str(ve)}")
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(f"Error: {str(e)}")
        }

    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=obfuscated_file.getvalue().encode('utf-8'))    
    logger.info(f"Processing file: {file_to_obfuscate}")

    return {
        'statusCode': 200,
        'body': 'File obfuscated successfully'
    }

