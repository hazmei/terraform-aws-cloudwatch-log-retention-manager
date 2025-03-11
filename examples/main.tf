provider "aws" {
  region = local.region

  # Make it faster by skipping something
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
  skip_requesting_account_id  = true
}

locals {
  name   = "ex-${basename(path.cwd)}"
  region = "eu-west-1"

  tags = {
    Example    = local.name
    GithubRepo = "terraform-aws-solutions"
    GithubOrg  = "terraform-aws-modules"
  }
}

####################################################
# Lambda Function triggered by EventBridge Schedule
####################################################

module "cloudwatch_log_retention_manager" {
  source = "../."

  name = local.name

  # Create package from the source (requires Python)
  #  create_package = true

  # Disable creation of the package to use the package distributed in the module
  create_package = false

  environment_variables = {
    RETAIN_DAYS       = 90
    LOG_GROUPS_TO_SET = "/aws/lambda/sqs-loader" # set to limit which log groups to set the retention in days if it wasn't specified
  }

  schedule_expression = "rate(6 hours)"

  tags = local.tags
}
