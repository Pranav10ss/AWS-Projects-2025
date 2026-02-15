resource "aws_vpc" "aws_vpc" {
  cidr_block           = "10.16.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "awsVPC"
  }
}

resource "aws_internet_gateway" "aws_igw" {
  vpc_id = aws_vpc.aws_vpc.id

  tags = {
    Name = "awsIGW"
  }
}

resource "aws_route_table" "aws_public_rt" {
  vpc_id = aws_vpc.aws_vpc.id

  tags = {
    Name = "awsPublicRT"
  }
}

resource "aws_route_table" "aws_private_rt" {
  vpc_id = aws_vpc.aws_vpc.id

  tags = {
    Name = "awsPrivateRT"
  }
}

resource "aws_route" "aws_public_default_route" {
  route_table_id         = aws_route_table.aws_public_rt.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.aws_igw.id
}

resource "aws_subnet" "aws_public_a" {
  vpc_id                  = aws_vpc.aws_vpc.id
  cidr_block              = "10.16.48.0/20"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "aws-publicA"
  }
}

resource "aws_subnet" "aws_public_b" {
  vpc_id                  = aws_vpc.aws_vpc.id
  cidr_block              = "10.16.112.0/20"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "aws-publicB"
  }
}

resource "aws_subnet" "aws_private_a" {
  vpc_id            = aws_vpc.aws_vpc.id
  cidr_block        = "10.16.32.0/20"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "aws-privateA"
  }
}

resource "aws_subnet" "aws_private_b" {
  vpc_id            = aws_vpc.aws_vpc.id
  cidr_block        = "10.16.96.0/20"
  availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name = "aws-privateB"
  }
}

resource "aws_route_table_association" "aws_public_a_assoc" {
  subnet_id      = aws_subnet.aws_public_a.id
  route_table_id = aws_route_table.aws_public_rt.id
}

resource "aws_route_table_association" "aws_public_b_assoc" {
  subnet_id      = aws_subnet.aws_public_b.id
  route_table_id = aws_route_table.aws_public_rt.id
}

resource "aws_route_table_association" "aws_private_a_assoc" {
  subnet_id      = aws_subnet.aws_private_a.id
  route_table_id = aws_route_table.aws_private_rt.id
}

resource "aws_route_table_association" "aws_private_b_assoc" {
  subnet_id      = aws_subnet.aws_private_b.id
  route_table_id = aws_route_table.aws_private_rt.id
}
