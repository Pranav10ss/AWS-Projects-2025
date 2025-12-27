terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# IAM Role required for the Lambda Function
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for lambda to access Bedrock Knowledge base
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "bedrock:Retrieve",
          "bedrock:RetrieveAndGenerate",
          "bedrock:InvokeModel"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# Lambda Function to query Bedrock Knowledge base
resource "aws_lambda_function" "kb_query" {
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256

  function_name    = "${var.project_name}-kb-query"
  role             = aws_iam_role.lambda_role.arn
  handler          = "index.handler"
  runtime          = "python3.11"
  timeout          = 30

  environment {
    variables = {
      KNOWLEDGE_BASE_ID = var.knowledge_base_id
      BEDROCK_MODEL_ARN = var.bedrock_model_id
    }
  }
}

# API Gateway to trigger the Lambda Function\
resource "aws_apigatewayv2_api" "kb_api" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["content-type"]
  }
}

resource "aws_apigatewayv2_stage" "kb_api_stage" {
  api_id      = aws_apigatewayv2_api.kb_api.id
  name        = "prod"
  auto_deploy = true
}

resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id           = aws_apigatewayv2_api.kb_api.id
  integration_type = "AWS_PROXY"
  integration_uri  = aws_lambda_function.kb_query.invoke_arn
}

resource "aws_apigatewayv2_route" "query_route" {
  api_id    = aws_apigatewayv2_api.kb_api.id
  route_key = "POST /query"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# permission to grant API Gateway to invoke the Lambda Function
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.kb_query.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.kb_api.execution_arn}/*/*"
}