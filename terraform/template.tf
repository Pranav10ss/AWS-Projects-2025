resource "local_file" "frontend_config" {
  filename = "${path.module}/../frontend/config.js"

  content = templatefile("${path.module}/../frontend/config.js.tpl", {
    api_url = "${aws_apigatewayv2_api.kb_api.api_endpoint}/prod/query"
  })
}