# GDPR Obfuscator Project


## Table of Contents
1. [Overview of the GDPR Obfuscator Project](#overview-of-the-gdpr-obfuscator-project)
   - [Context](#context)
   - [Assumptions and Prerequisites](#assumptions-and-prerequisites)
   - [High-Level Desired Outcome](#high-level-desired-outcome)
2. [Installation Instructions](#installation-instructions)
   - [Prerequisites](#prerequisites)
3. [Testing](#testing)
4. [Usage Instructions](#usage-instructions)
   - [Command-Line Usage](#use-of-the-gdpr-obfuscator-from-the-command-line)
   - [AWS Lambda Usage](#use-of-the-gdpr-obfuscator-from-a-lambda-function-in-an-aws-account)
     - [Custom Lambda Function](#using-a-custom-lambda-function)
     - [Terraform Integration](#using-the-provided-terraform-blueprint)
     - [Triggering the Lambda Function](#triggering-the-lambda-function)
5. [Future Enhancements](#future-enhancements)


## Overview of the GDPR Obfuscator Project
### Context

The purpose of this project is to create a general-purpose tool to process data being ingested into AWS and intercept personally identifiable information (PII). 
There is a requirement under GDPR to ensure that any data containing information that can be used to identify an individual is anonymized.

### Assumptions and Prerequisites

- Data is stored in **CSV format** in an AWS S3 bucket.
- Fields containing GDPR-sensitive data are known and will be supplied in advance.
- Data records will be supplied with a **primary key**.

### High-Level Desired Outcome

This tool will be integrated as a library module into a Python codebase. It will be supplied with:

- The S3 location of a file containing sensitive information.
- The names of the fields that need to be obfuscated.

The tool will process the input file and replace sensitive data with obfuscated strings.
The calling procedure will handle saving the output to its destination.
It is expected that the tool will be deployed within the AWS account.

#### Input Example:
The tool will be invoked by sending a JSON string that contains:
- `file_to_obfuscate`: The S3 location of the required CSV file.
- `pii_fields`: A list of the fields that need to be obfuscated.

Example input:
```json
{
  "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
  "pii_fields": ["name", "email_address"]
}
```

##### Target CSV File Example:

```
student_id,name,course,cohort,graduation_date,email_address
1234,'John Smith','Software','2024-03-31','j.smith@email.com'
```

##### Obfuscated Output Example:

```
student_id,name,course,cohort,graduation_date,email_address
1234,'***','Software','2024-03-31','***'
```

The output will be a byte-stream representation of the file, compatible with the boto3 S3 PutObject function.


## Installation Instructions

### Prerequisites

- Python 3.x: ensure you have Python installed. Check version using

```
python --version 
```

or

```
python3 --version 
```

- Install required libraries
```
make requirements
make dev-setup
make upgrade-libraries
pip install -r requirements.txt
```

### Testing

To run unit tests run:
```
make unit-test
```

## Usage instructions

### Use of the GDPR Obfuscator from the command line

Run any of these lines, depending on the file you want to use for demonstration purposes:

- Data file with 2 fields:
```
python obfuscator.py '{ "file_to_obfuscate": "../data/simple.csv", "pii_fields": ["name", "email_address"] }'
```

- Data file with 3 fields:
```
python obfuscator.py '{ "file_to_obfuscate": "../data/medium.csv", "pii_fields": ["name", "email_address"] }'
```


### Use of the GDPR Obfuscator from a Lambda Function in an AWS Account

You need an active AWS account with credentials (access keys or IAM roles) that have permissions to read and write to the required S3 bucket.

You can integrate the GDPR Obfuscator into an AWS Lambda function in two ways:

1. Using a Custom Lambda Function:
- Include the gdpr_obfuscator library as a Lambda layer.
- Invoke the function manually or through another service.

2. Using the Provided Terraform Blueprint:
- Ensure Terraform is installed.
- Navigate to the terraform directory and execute the following commands:

```
terraform init
terraform plan
terraform apply
```

#### Triggering the lambda function:

1. S3 Trigger Example

To test an S3 event trigger, use the following test example. Replace [BUCKET_NAME] with your bucket's name:
```
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "[BUCKET_NAME]"
        },
        "object": {
          "key": "file.csv"
        }
      }
    }
  ]
}
```

By default, the PII fields for this test are name and email_address.
Modify these fields in the blueprint if necessary.


2. Other Trigger Methods

You can use other tools (e.g., EventBridge, Step Functions, or Airflow) to invoke the Lambda function with this test example:

```
{
  "file_to_obfuscate": "s3://[BUCKET_NAME]/file.csv",
  "pii_fields": [
    "name",
    "email_address"
  ]
}
```

## Future Enhancements

1. **Support for Additional File Formats**: Extend the tool to handle JSON, Parquet, and other file formats.
2. **Customizable Obfuscation Logic**: Allow users to define custom anonymization rules for specific fields.
3. **Field Auto-Detection**: Implement a feature to automatically detect PII fields using heuristics or machine learning.
4. **Performance Optimization**: Scale processing to handle larger files efficiently.
5. **Integration with Data Pipelines**: Provide out-of-the-box support for integration with popular data processing frameworks like Apache Spark or AWS Glue.
