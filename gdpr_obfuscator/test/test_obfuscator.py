import pytest
import os
import boto3
import json
from moto import mock_aws
from gdpr_obfuscator.obfuscator import Obfuscator


@pytest.fixture(scope="class")
def aws_credentials():
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="function")
def s3_client(aws_credentials):
    with mock_aws():
        yield boto3.client("s3", region_name="eu-west-2")


def json_string_with_valid_s3_file(s3_client, bucket_name:str, file_name:str, pii_fields:list=None):
    # Mock S3 bucket and object with explicit region
    s3_client.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={'LocationConstraint': "eu-west-2"}
    )

    # Mock a valid file to the bucket
    s3_client.put_object(Bucket=bucket_name, Key=file_name, Body="test data")
  
    # If pii_fields are defined then use them in the json_string
    pii_fields_str = f'"pii_fields": {json.dumps(pii_fields)}' if pii_fields else ""

    # The trailing comma is only added if pii_fields is present (not empty)
    json_string = f'{{"file_to_obfuscate": "s3://{bucket_name}/{file_name}"{"," if pii_fields_str else ""} {pii_fields_str}}}'
    return json_string


class TestObfuscator:

    def test_obfuscator_throws_an_error_with_no_argument(self):
        with pytest.raises(TypeError):
            Obfuscator()

    def test_obfuscator_throws_an_error_with_an_empty_json_script(self):
        json_string = "{}"
        with pytest.raises(KeyError, match="Key 'file_to_obfuscate' is missing in the JSON string"):
            Obfuscator(json_string)

    def test_obfuscator_throws_an_error_with_a_json_script_malformed(self):
        json_string = "{asdf}"
        with pytest.raises(json.JSONDecodeError):
            Obfuscator(json_string)

    def test_obfuscator_throws_an_error_with_a_json_script_with_only_one_correct_key_but_no_value(self):
        json_string = """{
            "file_to_obfuscate"
        }"""
        with pytest.raises(json.JSONDecodeError):
            Obfuscator(json_string)

    def test_obfuscator_throws_an_error_with_a_json_script_with_only_one_correct_key_but_malformed(self):
        json_string = """{
            "file_to_obfuscate":
        }"""
        with pytest.raises(json.JSONDecodeError):
            Obfuscator(json_string)

    def test_obfuscator_throws_an_error_with_a_json_script_with_only_one_correct_key_and_empty_value(self):
        json_string = """{
            "file_to_obfuscate":""
        }"""
        with pytest.raises(ValueError, match="The field 'file_to_obfuscate' cannot be empty"):
            Obfuscator(json_string)

    def test_obfuscator_throws_an_error_with_a_json_script_with_invalid_file_to_obfuscate(self):
        json_string = """{
            "file_to_obfuscate":"asdf"
        }"""

        with pytest.raises(ValueError):
            Obfuscator(json_string)


    def test_obfuscator_throws_an_error_with_a_json_script_with_invalid_s3_file(self, s3_client):

        bucket_name = "my-ingestion-bucket"
        file_name = "nonexistent-file.csv"

        # Mock S3 bucket and object with explicit region
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': "eu-west-2"}
        )

        # Mock a non existing file
        json_string = f'{{"file_to_obfuscate": "s3://{bucket_name}/{file_name}"}}'

        expected_message = f"The file 's3://{bucket_name}/{file_name}' does not exist or is not a valid file"
        with pytest.raises(ValueError, match=expected_message):
            Obfuscator(json_string)
    

    def test_obfuscator_ok_json_script_with_valid_s3_file_no_pii_fields(self, s3_client):
        bucket_name = "my-ingestion-bucket"
        file_name = "existent-file.csv"

        json_string = json_string_with_valid_s3_file(s3_client, bucket_name, file_name)
        obfuscator = Obfuscator(json_string)
        assert obfuscator.file_to_obfuscate == f"s3://{bucket_name}/{file_name}"
        assert obfuscator.pii_fields == []


    def test_obfuscator_ok_json_script_with_valid_s3_file_and_pii_fields(self, s3_client):
        bucket_name = "my-ingestion-bucket"
        file_name = "existent-file.csv"
        pii_fields = ["name", "email_address"]

        json_string = json_string_with_valid_s3_file(s3_client, bucket_name, file_name, pii_fields)
        obfuscator = Obfuscator(json_string)
        assert obfuscator.pii_fields == pii_fields