terraform {
  backend "s3" {
    bucket  = "dms-project-tfstate-bucket"
    key     = "state.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
}