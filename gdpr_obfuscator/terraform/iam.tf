resource "aws_iam_role" "iam_for_lambda" {
  name = "lambda_handler_role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

# IAM policy for lambda function to assume a role with permissions to access S3 
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

# IAM role withe access to get all objects of an S3 bucket
resource "aws_iam_role_policy" "lambda_s3_access" {
  name   = "LambdaS3AccessPolicy"
  role   = aws_iam_role.iam_for_lambda.name
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["s3:GetObject", "s3:PutObject"],
        Resource = [
          "${aws_s3_bucket.my_bucket.arn}/*"
        ]
      }
    ]
  })
}
