# GDPR Obfuscator Project

## Overview of the GDPR Obfuscator Project
### Context

The purpose of this project is to create a general-purpose tool to process data being ingested into AWS and intercept personally identifiable information (PII). 
There is a requirement under GDPR to ensure that any data containing information that can be used to identify an individual is anonymized.

### Assumptions and Prerequisites

- Data is stored in CSV in an AWS S3 bucket.
- Fields containing GDPR-sensitive data are known and will be supplied in advance.
- Data records will be supplied with a primary key.

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

- AWS account: you need an active AWS account with credentials (access keys or IAM roles) that have permissions to read and write to the required S3 bucket.


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

You can use your own lambda function, adding the gdpr_obfuscator as a library in a layer.

If you want to use a blueprint to start using the obfuscator on a lambda function, then you can recreate the function by using Terraform.
For this option, you need to have Terraform installed.

Go to the directory "terraform" and execute:
```
terraform init
terraform plan
terraform apply
```

Invoke the lambda with a test:
(Replace [BUCKET_NAME] with the name of your bucket)


- Test S3 trigger:

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

By default, the pii_fields for an test S3 trigger are "name" and "email_address".
If you want to change them, go to the blueprint and modify accordingly.


- Any other tool such as EventBridge, Step Functions, or Airflow as a trigger:

```
{
  "file_to_obfuscate": "s3://[BUCKET_NAME]/file.csv",
  "pii_fields": [
    "name",
    "email_address"
  ]
}
```