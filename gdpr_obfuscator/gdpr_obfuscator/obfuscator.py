import json
import os
import boto3
from urllib.parse import urlparse
from botocore.exceptions import ClientError

class Obfuscator:
    """
    """
    def __init__(self, json_string:str):
       
        # If there the json string is empty then a Value error is raised
        if not json_string:
            raise ValueError("JSON string cannot be empty")

        # Set attributes
        self.__pii_fields = []
        file_location, fields = self.__get_data(json_string)
        self.file_to_obfuscate = file_location
        self.pii_fields = fields

    def __get_data(self, json_string:str):
        try:
            # Parse the json string for file location and fields to obfuscate
            data = json.loads(json_string)

        except json.JSONDecodeError as e:
            
            # Raise the error with the element that causes the error and the position
            raise json.JSONDecodeError("Invalid JSON string provided", json_string, e.pos) from e
        
        # If the key "file_to_obfuscate" is not present then raise a Key Error
        if "file_to_obfuscate" not in data:
            raise KeyError("Key 'file_to_obfuscate' is missing in the JSON string")
        
        # Get the value of the key
        file_name = data.get("file_to_obfuscate", "")

        # If empty, raise a value error
        if not file_name:
            raise ValueError("The field 'file_to_obfuscate' cannot be empty")
        
        
        pii_fields = data.get("pii_fields", [])
        return file_name, pii_fields


    @property
    def pii_fields(self):
        return self.__pii_fields
    

    @pii_fields.setter
    def pii_fields(self, value:list):
        self.__pii_fields = value


    @property
    def file_to_obfuscate(self):
        return self.__file_to_obfuscate


    @file_to_obfuscate.setter
    def file_to_obfuscate(self, file_name:str):
        """
        Sets the file to be obfuscated by validating its existence and checking if it is a valid file in an S3 bucket.

        This method validates whether the provided file name is a valid file and checks if it exists in a S3 bucket.
        If the file is invalid or does not exist, it raises a `ValueError` with a descriptive error message.

        Args:
            file_name (str): The name or S3 URI of the file to be obfuscated.

        Raises:
            ValueError: If the file is not valid, does not exist, or is not found in the S3 bucket.
        
        Side Effects:
            If the file is valid, the provided file name is stored in the `__file_to_obfuscate` attribute for further processing.

        Example:
            file_name = "s3://my-bucket/path/to/file.csv"
            obfuscator.file_to_obfuscate(file_name)
        """

        # If not a valid file, raise an error
        if not self.__is_valid_file(file_name):
            raise ValueError(f"The file '{file_name}' does not exist or is not a valid file")
        

        # Check if the file exists in the data bucket
        s3 = boto3.client("s3")
        bucket_name, key = self.__parse_s3_uri(file_name)

        try:
            # Get the object from the bucket
            s3.head_object(Bucket=bucket_name, Key=key)
        except ClientError as e:
            # Raise an error if the file does not exist
            raise ValueError(f"File '{file_name}' not found in S3 bucket '{bucket_name}'")

        # Set the attribute
        self.__file_to_obfuscate = file_name


    def __is_valid_file(self, file_path: str) -> bool:
        """
        Checks if the given file path is a valid file.
        Checks both local and S3 paths.
        """

        if file_path.startswith('s3://'):
            # Check if it's an S3 URL
            return self.__is_valid_s3_file(file_path)
        else:
            # Check if it's a local file
            return os.path.isfile(file_path)
        

    def __is_valid_s3_file(self, s3_url: str) -> bool:
        """
        Checks if the file exists in an S3 bucket.
        """
        s3 = boto3.client('s3')
        parsed_url = urlparse(s3_url)
        bucket_name = parsed_url.netloc
        key = parsed_url.path.lstrip('/')

        try:
            s3.head_object(Bucket=bucket_name, Key=key)
            return True
        except s3.exceptions.ClientError:
            return False
        

    def __parse_s3_uri(self, s3_uri: str):
        """
        Parses the S3 URI and returns the bucket name and key.
        """
        if not s3_uri.startswith("s3://"):
            raise ValueError("Invalid S3 URI")
        
        s3_uri = s3_uri[5:]
        bucket_name, key = s3_uri.split("/", 1)
        return bucket_name, key