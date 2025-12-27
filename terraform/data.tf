data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../Lambda"
  output_path = "${path.module}/lambda_function.zip"
}