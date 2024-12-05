variable "my_bucket_prefix" {
  type = string
  default = "my-bucket-"
}

variable "lambda_obfucator" {
  type = string
  default = "lambda_obfuscator"
}

variable "python_version" {
    type = string
    default = "python3.12"
}