data "archive_file" "lambda_obfuscator" {
    type        = "zip"
    output_file_mode = "0666"
    source_file = "${path.module}/../gdpr_obfuscator/lambda_obfuscator.py"
    output_path = "${path.module}/../gdpr_obfuscator/lambda_obfuscator.zip"
}

data "archive_file" "lambda_layer" {
    type = "zip"
    output_file_mode = "0666"
    source_dir = "${path.module}/../layer/"
    output_path = "${path.module}/../layer.zip"
}

resource "aws_lambda_function" "lambda_obfuscator" {
    function_name = "${var.lambda_obfucator}"
    role = aws_iam_role.iam_for_lambda.arn
    handler = "${var.lambda_obfucator}.lambda_handler"
    runtime = var.python_version
    timeout = 30
    filename = data.archive_file.lambda_obfuscator.output_path
    source_code_hash = data.archive_file.lambda_obfuscator.output_base64sha256

    environment {
      variables = {
        S3_BUCKET_NAME = aws_s3_bucket.my_bucket.bucket
      }
    }

    layers = [
        aws_lambda_layer_version.libraries_layer.arn
    ]
}

# Layer with the Obfuscator Class
resource "aws_lambda_layer_version" "libraries_layer" {
    layer_name = "libraries_layer"
    compatible_runtimes = [var.python_version]
    depends_on = [ aws_s3_object.lambda_code ]
    filename = data.archive_file.lambda_layer.output_path
}

# Allow S3 to invoke lambda
resource "aws_lambda_permission" "allow_s3_to_invoke_lambda" {
    statement_id = "AllowS3InvokeLoadLambda"
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.lambda_obfuscator.function_name
    principal = "s3.amazonaws.com"
    source_arn = aws_s3_bucket.my_bucket.arn
}