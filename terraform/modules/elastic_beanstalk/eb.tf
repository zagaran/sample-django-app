locals {
  # This file is the equivalent of running `eb config -d <environment_name>` on an existing environment and taking the output
  eb_web_config = yamldecode(file("${path.module}/eb_web_config.yaml")).settings

  eb_web_static_settings = flatten([
    for namespace, options in local.eb_web_config : [
      for name, value in options : {
        # Some pieces of the export have extraneous substrings before the namespace name, ex. "AWSEBAutoScalingScaleUpPolicy."
        namespace = startswith(namespace, "aws:") ? namespace : split(".", namespace)[1]
        name = name
        value = value
      }
      # SecurityGroups are set up at launch time
      # ImageId is derived from platform version
      # SSLCertificateArns are set up at launch time
      # null and blank settings cause Terraform to error
      # Namespaces starting with a colon are settings of the shared load balancer
      if name != "SecurityGroups" && name != "ImageId" && name != "SSLCertificateArns" && value != null && value != "" && ! startswith(namespace, ":")
    ]
  ])
}

locals {
  # This file is the equivalent of running `eb config -d <environment_name>` on an existing environment and taking the output
  eb_worker_config = yamldecode(file("${path.module}/eb_worker_config.yaml")).settings

  # Static EB settings defined by the config yaml
  eb_worker_static_settings = flatten([
    for namespace, options in local.eb_worker_config : [
      for name, value in options : {
        # Some pieces of the export have extraneous substrings before the namespace name, ex. "AWSEBAutoScalingScaleUpPolicy."
        namespace = startswith(namespace, "aws:") ? namespace : split(".", namespace)[1]
        name = name
        value = value
      }
      # SecurityGroups are set up at launch time
      # ImageId is derived from platform version
      # SSLCertificateArns are set up at launch time
      # null and blank settings cause Terraform to error
      # Namespaces starting with a colon are settings of the shared load balancer
      if name != "SecurityGroups" && name != "ImageId" && name != "SSLCertificateArns" && value != null && value != "" && ! startswith(namespace, ":")
    ]
  ])
}

locals {
  # dynamic settings defined by module inputs
  eb_web_dynamic_settings = [
    {
      namespace = "aws:elasticbeanstalk:container:python"
      name = "NumProcesses"
      value = var.num_processes
    }, {
      namespace = "aws:ec2:instances"
      name = "InstanceTypes"
      value = var.instance_type
    }, {
      namespace = "aws:autoscaling:launchconfiguration"
      name = "InstanceType"
      value = var.instance_type
    }, {
      namespace = "aws:autoscaling:asg"
      name = "MinSize"
      value = var.min_instances
    }, {
      namespace = "aws:autoscaling:asg"
      name = "MaxSize"
      value = var.max_instances
    }, {
      namespace = "aws:elasticbeanstalk:command"
      name = "DeploymentPolicy"
      value = var.deployment_policy
    }, {
      namespace = "aws:ec2:vpc"
      name = "ELBSubnets"
      value = join(",", var.vpc_private_subnet_ids)
    }, {
      namespace = "aws:ec2:vpc"
      name = "Subnets"
      value = join(",", var.vpc_private_subnet_ids)
    }, {
      namespace = "aws:elbv2:loadbalancer"
      name = "SharedLoadBalancer"
      value = var.load_balancer_arn
    }, {
      namespace = "aws:elbv2:loadbalancer"
      name = "SecurityGroups"
      value = var.load_balancer_security_group_id
    }, {
      namespace = "aws:ec2:vpc"
      name = "VPCId"
      value = var.vpc_id
    }, {
      namespace   = "aws:elbv2:listener:443"
      name = "SSLCertificateArns"
      value = var.certificate_arn
    }
  ]
  eb_web_dynamic_keys = toset([
    for setting in local.eb_web_dynamic_settings :
      format("%s/%s", setting.namespace, setting.name)
  ])
  eb_web_filtered_static_settings = [
    for setting in local.eb_web_static_settings :
      # Ensure each setting only appears once or Terraform will pick at random from repeated settings
      setting if ! contains(local.eb_web_dynamic_keys, format("%s/%s", setting.namespace, setting.name))
  ]
  eb_web_settings = concat(
    local.eb_web_dynamic_settings,
    local.eb_web_filtered_static_settings
  )
}


locals {
  # dynamic settings defined by module inputs
  eb_worker_dynamic_settings = [
    {
      namespace = "aws:elasticbeanstalk:container:python"
      name = "NumProcesses"
      value = var.num_processes
    }, {
      namespace = "aws:ec2:instances"
      name = "InstanceTypes"
      value = var.instance_type
    }, {
      namespace = "aws:autoscaling:launchconfiguration"
      name = "InstanceType"
      value = var.instance_type
    }, {
      namespace = "aws:autoscaling:asg"
      name = "MinSize"
      value = var.min_instances
    }, {
      namespace = "aws:autoscaling:asg"
      name = "MaxSize"
      value = var.max_instances
    }, {
      namespace = "aws:elasticbeanstalk:command"
      name = "DeploymentPolicy"
      value = var.deployment_policy
    }, {
      namespace = "aws:ec2:vpc"
      name = "ELBSubnets"
      value = join(",", var.vpc_private_subnet_ids)
    }, {
      namespace = "aws:ec2:vpc"
      name = "Subnets"
      value = join(",", var.vpc_private_subnet_ids)
    }, {
      namespace = "aws:ec2:vpc"
      name = "VPCId"
      value = var.vpc_id
    }, {
      namespace = "aws:elasticbeanstalk:sqsd"
      name = "WorkerQueueUrl"
      value = aws_sqs_queue.worker_queue.url
    }
  ]
  eb_worker_dynamic_keys = toset([
    for setting in local.eb_worker_dynamic_settings :
    format("%s%s", setting.namespace, setting.name)
  ])
  eb_worker_filtered_static_settings = [
    for setting in local.eb_worker_static_settings :
    # Ensure each setting only appears once or Terraform will pick at random from repeated settings
    setting if ! contains(local.eb_worker_dynamic_keys, format("%s%s", setting.namespace, setting.name))
  ]
  eb_worker_settings = concat(
    local.eb_worker_dynamic_settings,
    local.eb_worker_filtered_static_settings
  )
}

data "aws_elastic_beanstalk_solution_stack" "python_3_11" {
  most_recent = true
  name_regex = "^64bit Amazon Linux 2023 (.*) Python 3.11$"
}

resource "aws_elastic_beanstalk_environment" "eb_web" {
  name = format("%s-web", lower(var.environment_name))
  application = "var.eb_application_name"
  solution_stack_name = data.aws_elastic_beanstalk_solution_stack.python_3_11.name
  cname_prefix = var.cname_prefix != "" ? var.cname_prefix : lower(var.environment_name)
  tier = "WebServer"

  # Dynamically apply settings defined in locals above
  dynamic setting {
    for_each = local.eb_web_settings
    content {
      namespace = setting.value["namespace"]
      name = setting.value["name"]
      value = setting.value["value"]
    }
  }

  # Settings overrides
  lifecycle {
    # Auto-environment updates change solution_stack_name
    # Don't trigger terraform to recreate environments when settings are changed via config changes in `.ebextensions` directory
    ignore_changes = [setting, solution_stack_name]
  }
}

resource "aws_elastic_beanstalk_environment" "eb_worker" {
  count = var.create_worker
}


