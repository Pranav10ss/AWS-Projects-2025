resource "aws_instance" "db" {
  ami                    = data.aws_ssm_parameter.amzn2.value
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.onprem_public.id
  vpc_security_group_ids = [aws_security_group.onprem_db.id]
  iam_instance_profile   = aws_iam_instance_profile.onprem_profile.name

  user_data = file("${path.module}/user-data/db.sh")

  tags = {
    Name = "DB"
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ssm_parameter.amzn2.value
  instance_type          = "t3.micro"
  subnet_id              = aws_subnet.onprem_public.id
  vpc_security_group_ids = [aws_security_group.onprem_web.id]
  iam_instance_profile   = aws_iam_instance_profile.onprem_profile.name

  user_data = templatefile("${path.module}/user-data/web.sh", {
    db_host     = aws_instance.db.private_ip
    db_name     = var.db_name
    db_user     = var.db_user
    db_password = var.db_password
  })

  tags = {
    Name = "Web"
  }
}