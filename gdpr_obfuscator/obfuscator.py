import json
import os
import boto3
import csv
import io
from urllib.parse import urlparse
import argparse


class Obfuscator:
    """ """

    def __init__(self, json_string: str):
        """
        Initializes an instance of the class by parsing the provided JSON string.

        The constructor parses the given JSON string to extract the file location
        and optional fields to obfuscate. If the JSON string is empty, a ValueError
        is raised. The extracted information is stored in instance variables.

        Arguments:
            json_string (str): A JSON-formatted string containing the file location
            and optional fields to obfuscate. The string should include the key
            'file_to_obfuscate' and optionally 'pii_fields'.

        Raises:
            ValueError: If the provided JSON string is empty.
            KeyError: If the 'file_to_obfuscate' key is missing in the JSON string.
            ValueError: If the 'file_to_obfuscate' key is empty in the JSON string.
        """

        # If the json string is empty then a Value error is raised
        if not json_string:
            raise ValueError("JSON string cannot be empty")

        # Set attributes
        self.__pii_fields = []
        file_location, fields = self.__get_data(json_string)
        self.file_to_obfuscate = file_location
        self.pii_fields = fields

    def __get_data(self, json_string: str) -> tuple[str, list]:
        """
        Parses a JSON string to extract the file location and optional fields to obfuscate.

        This function loads a JSON string, checks for the presence of required keys,
        and returns the file path and a list of fields to obfuscate. If the necessary
        keys are missing or invalid, appropriate exceptions are raised.

        Arguments:
            json_string (str): A JSON-formatted string containing the file path
            and optional fields to obfuscate. The string must include the key
            'file_to_obfuscate' and optionally 'pii_fields'.

        Returns:
            tuple: A tuple containing:
                - file_name (str): The value associated with the 'file_to_obfuscate' key.
                - pii_fields (list): A list of fields to obfuscate, defaults to an empty list
                if the key 'pii_fields' is missing.

        Raises:
            json.JSONDecodeError: If the input string is not a valid JSON.
            KeyError: If the key 'file_to_obfuscate' is missing from the JSON string.
            ValueError: If the 'file_to_obfuscate' key is empty.
        """
        try:
            # Parse the json string for file location and fields to obfuscate
            data = json.loads(json_string)

        except json.JSONDecodeError as e:

            # Raise the error with the element that causes the error and the position
            raise json.JSONDecodeError(
                "Invalid JSON string provided", json_string, e.pos
            ) from e

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
    def pii_fields(self, value: list):
        self.__pii_fields = value

    @property
    def file_to_obfuscate(self):
        return self.__file_to_obfuscate

    @file_to_obfuscate.setter
    def file_to_obfuscate(self, file_name: str):
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
            raise ValueError(
                f"The file '{file_name}' does not exist or is not a valid file"
            )

        self.__file_to_obfuscate = file_name

    def __is_valid_file(self, file_path: str) -> bool:
        """
        Determines if the given file path is valid.

        This function checks the validity of the file path by determining if it
        points to a local file or a file stored in an S3 bucket. If the path starts
        with "s3://", it is treated as an S3 file path and validated accordingly.
        Otherwise, it checks the file's existence as a local file.

        Arguments:
            file_path (str): The path to the file to validate. It can be either a
            local file path or an S3 file path.

        Returns:
            bool: True if the file path points to an existing and non-empty local 
            file or a valid S3 key. False otherwise.
        """

        if file_path.startswith("s3://"):
            # Check if it's an S3 URL
            return self.__is_valid_s3_file(file_path)
        else:
            # Check if it's a local file
            if os.path.isfile(file_path):
                if os.path.getsize(file_path) == 0:
                    return False
                return True
            return False

    def __is_valid_s3_file(self, s3_url: str) -> bool:
        """
        Validates if a given S3 URL points to an existing file in an AWS S3 bucket.

        Args:
            s3_url (str): The URL of the file (key) in the S3 bucket, typically in the format 's3://bucket-name/key'.

        Returns:
            bool: True if the file exists and is accessible in the specified S3 bucket, otherwise False.
        """
        s3 = boto3.client("s3")
        bucket_name, key = self.__get_bucket_name_and_key(s3_url)

        try:
            s3.head_object(Bucket=bucket_name, Key=key)
            return True
        except s3.exceptions.ClientError:
            return False

    def __get_bucket_name_and_key(self, s3_url: str) -> tuple[str, str]:
        """
        Extracts the bucket name and key from an S3 URL.

        Args:
            s3_url (str): The S3 URL in the format 's3://bucket-name/key'.

        Returns:
            tuple: A tuple containing the bucket name (str) and the key (str).

        Example:
            s3_url = "s3://my-bucket/my-folder/my-file.csv"
            bucket_name, key = self.__get_bucket_name_and_key(s3_url)
            # bucket_name = "my-bucket"
            # key = "my-folder/my-file.csv"
        """
        parsed_url = urlparse(s3_url)
        bucket_name = parsed_url.netloc
        key = parsed_url.path.lstrip("/")
        return bucket_name, key

    def obfuscate(self) -> io.StringIO:
        """
        Obfuscates the PII fields in a CSV file.
        Each PII field will be replaced with '***'.

        Returns:
            A byte-stream representation of the obfuscated file.
        """
        s3 = boto3.client("s3")

        if self.file_to_obfuscate.startswith("s3://"):
            bucket_name, file_name = self.__get_bucket_name_and_key(self.file_to_obfuscate)
            file_obj = s3.get_object(Bucket=bucket_name,Key=file_name)
            file_content = file_obj["Body"].read().decode("utf-8")
            file = io.StringIO(file_content)
        else:
            file = open(self.file_to_obfuscate, "r")

        # Create a byte stream
        byte_stream = io.StringIO()

        reader = csv.DictReader(file)
        rows = list(reader)
        fieldnames = reader.fieldnames

        # Process the rows and obfuscate PII fields
        for row in rows:
            for pii_field in self.pii_fields:
                if pii_field in row:
                    row[pii_field] = "***"

        # Writing the obfuscated data to the byte-stream
        writer = csv.DictWriter(byte_stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

        # Reset the pointer to the beginning of the byte stream
        byte_stream.seek(0)

        if not isinstance(file, io.StringIO):
            file.close()

        # Return the byte stream directly (no encoding needed)
        return byte_stream


def main():
    parser = argparse.ArgumentParser(
        description="Obfuscate PII fields in a CSV file using the Obfuscator class."
    )
    parser.add_argument(
        "json_string",
        type=str,
        help="JSON string containing 'file_to_obfuscate' and optional 'pii_fields'.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional path to save the obfuscated file. Defaults to stdout.",
    )

    args = parser.parse_args()

    try:
        # Create an instance of Obfuscator and process the file
        obfuscator = Obfuscator(args.json_string)
        obfuscated_file = obfuscator.obfuscate()

        # Save to file or print to stdout
        if args.output:
            with open(args.output, "w") as out_file:
                out_file.write(obfuscated_file.getvalue())
            print(f"Obfuscated file saved to {args.output}")
        else:
            print(obfuscated_file.getvalue())

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

