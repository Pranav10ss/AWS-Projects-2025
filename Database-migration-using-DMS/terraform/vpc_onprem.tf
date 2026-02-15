resource "aws_vpc" "onprem" {
  cidr_block           = "192.168.10.0/24"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "onpremVPC"
  }
}

resource "aws_vpc" "onprem" {
  cidr_block           = "192.168.10.0/24"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "onpremVPC"
  }
}

resource "aws_internet_gateway" "onprem_igw" {
  vpc_id = aws_vpc.onprem.id

  tags = {
    Name = "onpremIGW"
  }
}

resource "aws_subnet" "onprem_public" {
  vpc_id                  = aws_vpc.onprem.id
  cidr_block              = "192.168.10.0/24"
  map_public_ip_on_launch = true
  availability_zone       = data.aws_availability_zones.available.names[0]

  tags = {
    Name = "onprem-public"
  }
}

resource "aws_route_table" "onprem_public" {
  vpc_id = aws_vpc.onprem.id

  tags = {
    Name = "onpremPublicRT"
  }
}

resource "aws_route" "onprem_default" {
  route_table_id         = aws_route_table.onprem_public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.onprem_igw.id
}

resource "aws_route_table_association" "onprem_assoc" {
  subnet_id      = aws_subnet.onprem_public.id
  route_table_id = aws_route_table.onprem_public.id
}