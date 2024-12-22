provider "aws" {
    alias  = "region-2"
    region = "eu-west-2"
}

# S3 BUCKET
resource "aws_s3_bucket" "my_bucket" {
    bucket_prefix = var.my_bucket_prefix
}

# LAMBDA CODE
resource "aws_s3_object" "lambda_code" {
    bucket = aws_s3_bucket.my_bucket.id
    key = "code/gdpr_obfuscator.zip"
    source = "${path.module}/../gdpr_obfuscator/lambda_obfuscator.zip"
}

# # TRIGGER OF THE LAMBDA CODE THROUGH A NEW FILE IN THE S3 BUCKET
# resource "aws_s3_bucket_notification" "extract_bucket_notification" {
#     bucket = aws_s3_bucket.my_bucket.id

#     lambda_function {
#         lambda_function_arn = aws_lambda_function.lambda_obfuscator.arn
#         events = ["s3:ObjectCreated:*"]
#         filter_suffix = ".csv"
#     }
#     depends_on = [aws_lambda_permission.allow_s3_to_invoke_lambda]
# }