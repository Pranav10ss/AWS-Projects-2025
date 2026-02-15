output "api_endpoint" {
  description = "API Gateway endpoint URL"
  value       = aws_apigatewayv2_api.kb_api.api_endpoint
}

output "api_url" {
  description = "Full API URL for querying"
  value       = "${aws_apigatewayv2_api.kb_api.api_endpoint}/prod/query"
}

output "lambda_function_name" {
  description = "Lambda function name"
  value       = aws_lambda_function.kb_query.function_name
}

output "s3_bucket_name" {
  description = "S3 bucket name for frontend"
  value       = aws_s3_bucket.frontend.id
}

output "s3_website_url" {
  description = "S3 website endpoint"
  value       = "http://${aws_s3_bucket_website_configuration.frontend.website_endpoint}"
}

output "cloudfront_url" {
  description = "CloudFront distribution URL (HTTPS)"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "frontend_url" {
  description = "Frontend URL to access the application"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}