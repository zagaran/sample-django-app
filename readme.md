# Project Template and Optional Features

This project was created using https://github.com/zagaran/django-template

See the readme on [django-template](https://github.com/zagaran/django-template) for:
* Instructions on starting your own project
* An explanation of included features.

# Local Project Setup

Set up a Python virtual environment: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment

```bash
# Create environment config file.
cp config/.env.example config/.env

# Fill in appropriate environment values.
nano config/.env

# Install pip requirements.
pip install --upgrade pip
pip install -r requirements-dev.txt

# Apply migrations and sync database schema.
python manage.py migrate
# Install Node dependencies
npm install


# START_FEATURE sass_bootstrap
# Complie SCSS files
python manage.py compilescss
# END_FEATURE sass_bootstrap
```

To run the project:
```bash
python manage.py runserver_plus
```

To run the frontend with hotloading React assets:
1. Set `WEBPACK_LOADER_HOTLOAD=True` in `config/.env`
2. Run the following (in addition to `manage.py runserver_plus`):
    ```bash
    node_modules/nwb/lib/bin/nwb.js serve
    ```

To make a static build of the frontend (such as when doing development on
non-React parts of the codebase):
1. Set `WEBPACK_LOADER_HOTLOAD=False` in `config/.env`
2. Run the following:
    ```bash
    node_modules/nwb/lib/bin/nwb.js build --no-vendor
    ```

To access the database:
```bash
python manage.py shell_plus
```

To run the test suite:
```bash
python manage.py test
```

To get a test coverage report:
```bash
coverage run --source='.' manage.py test; coverage report
```

# Requirements

The project uses [pip-tools](https://github.com/jazzband/pip-tools) to manage requirements.  In addition, it has two requirements files:

* `requirements.txt`: this is for requirements that should be installed on servers.
* `requirements-dev.txt`: this is a superset of requirements.txt that should be used only for local development.  This includes tools that are not needed on server deployments of the codebase and thus omitted in `requirements.txt` to reduce extraneous server installs.

To add a new dependency to or update requirements, add the entry to requirements.in (if it's needed for the codebase to run) or requirements-dev.in (if it's just needed for development) and run `pip-compile` to generate new .txt files:
```bash
nano requirements.in  # Updating Python dependencies as needed
nano requirements-dev.in  # Updating Python dev dependencies as needed
pip-compile requirements.in --upgrade  # Generate requirements.txt with updated dependencies
pip-compile requirements-dev.in --upgrade  # Generate requirements-dev.txt with updated dependencies
```

# Settings

This project uses [django-environ](https://django-environ.readthedocs.io/en/latest/)
to read configuration from either `config/.env` (for local development)
or from environment varables (for server deployments).  For a list of settings,
see the `environ.Env(` object in [config/settings.py](config/settings.py).


# Project deployment infrastructure
## Elastic Beanstalk

The following Python packages are useful tools for interacting with AWS and Elastic Beanstalk.
Due to dependency conflicts, these should not be installed in your project's regular virtual environment,
and should instead either be installed globally or in a separate virtual environment that runs them:

```bash
pip install awscli  # For interacting with general AWS services (note, this package often has conflicts with its botocore dependency)
pip install awsebcli  # For interacting with Elastic Beanstalk (note, this package often has conflicts with its botocore dependency)
pip install eb-create-environment  # For automating the creation of Elastic Beanstalk applications
pip install eb-ssm  # For Elastic Beanstalk SSH functionality without requiring shared private keys
```

### Creating a new Elastic Beanstalk environment

To create a new Elastic Beanstalk environment, modify the contents of [.elasticbeanstalk/eb_create_environment.yml]([.elasticbeanstalk/eb_create_environment.yml]) and run `eb-create-environment -c .elasticbeanstalk/eb_create_environment.yml`.

See the docs for [eb-create-environment](https://github.com/zagaran/eb-create-environment/) for more details.

Then, add the following environment variables:
```
ALLOWED_HOSTS
SECRET_KEY
AWS_STORAGE_BUCKET_NAME
GOOGLE_OAUTH2_KEY
GOOGLE_OAUTH2_SECRET
SENTRY_DSN
DEFAULT_FROM_EMAIL
```

Following that, deploy your code to the environment (see below).

### Deploying code

To deploy new versions of your code to your environment, run `eb deploy <environment_name>` using the EB CLI to deploy your code to that environment.

See the [eb-cli](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html) docs on general command line usage of Elastic Beanstalk.

### SSH

To SSH into an Elastic Beanstalk Environment, use [eb-ssm](https://github.com/zagaran/eb-ssm).
## ECS
Deployment to ECS requires Docker and Terraform. The configuration includes E2E encryption. 

### Creating a new ECS environment
The terraform configuration for ECS deployments will create both a web and worker service, 
with a Redis instance to act as a task broker. To create a new environment, add a new directory to `terraform/envs` 
with a `main.tf` that references the `ecs_deployment` module. The deployment script assumes that the `environment_name`
parameter matches the directory name.

In the following steps, config variables go in `terraform/envs/<ENV_NAME>/main.tf`; most of them go in the definition 
of the `ecs_deployment` module.
Steps 1 - 4 may be shared between environments as appropriate.

1. Create a VPC and subnets (or use the default VPC). This is config var `ecs_deployment.vpc_id`.
1. Create an ECR repository. Add an appropriate lifecycle policy to remove untagged images (e.g. 90 days). This is config var `ecs_deployment.ecr_repository_name`.
3. Create a bucket for holding terraform config. This is config var `terraform.backend.bucket`.
4. Create an SES identity and from email (if using SES). The from email is config var `ecs_deployment.ses_from_email`.
5. Create an AWS certificate manager certificate for your domain. This is config var `ecs_deployment.certificate_manager_arn`.
6. Create a secrets manager secret containing the config parameters needed by the application. This is config var `ecs_deployment.web_config_secret_name`. 
   You do not need to include "DATABASE_URL", "SECRET_KEY", "AWS_STORAGE_BUCKET_NAME", "DEFAULT_FROM_EMAIL", or "CELERY_BROKER_URL" 
   as those are managed by terraform in `terraform/modules/ecs_deployment/secrets_manager.tf`
7. Fill in the remaining missing values in `terraform/envs/<ENV_NAME>/main.tf` (See TODOs for details)
8. Run terraform to set up that environment
   ```
   cd terraform/envs/<ENV_NAME>
   terraform init
   terraform plan
   terraform apply
   ```
   The initial service deployments will fail because they reference ECR images that don't exist, but this will be resolved by the next step.
9. Deploy your code using the steps described below. This will push the initial application image, start the server task(s), and run migrations.
10. Add a DNS entry from your domain name to the created load balancer

### Deploying code
To deploy new versions of your code to an ECS environment, use the included `deploy.py` script. 
You must have docker installed and running in order to run build steps in the script.
First fill in the missing constants at the top of that file, and then run the script:

```
python deploy.py <ENV_NAME>
```
This script will do the following:
1. Build the docker image using your local code version.
2. Push the docker image to the ECR location for the specified environment
3. Stop the running worker service
4. Run database migrations
5. Deploy to the running web service and restart the worker service

Run `python deploy.py --help` to see available options. You may choose to use an existing ECR image or skip migrations.

#### Note on E2E Encryption
The server self-signed SSL certificate is generated as part of Docker image creation. It is valid for 10 years and will 
be regenerated every time python packages are updated, or if the Docker cache is cleared for any reason.

### GitHub actions deployment
The project includes a GitHub action workflow to build and deploy the application. To configure this, you must create
an environment within the GitHub repository for each environment you wish to deploy to 
(Settings > Code & Automation > Environments) and add the following environment variables:
* `AWS_PROFILE_NAME`: This should match the profile name specified in `deploy.py`.
* `AWS_ROLE_TO_ASSUME`: This should be the result of running `terraform output github_actions_deployment_role_arn` 
   within the appropriate terraform environment

You can then trigger deployment from any branch by navigating to Actions > Build and deploy application > Run workflow 
and selecting the appropriate branch and environment. To add a new environment, make sure the deployment role name is 
provided to the `ecs_deployment` module in `main.tf`, add a new environment within GitHub as specified above, and add
a new environment option to `.github/workflows/build_and_deploy.yml` under `inputs`. The current supported environments 
are:
* staging

### SSH
To run a bash shell in an ECS environment, use `python deploy.py <ENV_NAME> ssh`.
By default, this will run in the worker environment. Use the `--web` argument to run on the web server instead.

### Worker tasks & status monitoring
Scheduled worker tasks should be registered in `tasks/tasks.py`. Other async tasks can be registered in a `tasks.py` 
file in any application.
Each worker task will automatically register a Sentry cron monitor the first time it runs. By default, monitors have a 
1-minute grace period, 30-minute timeout, and will register an issue after a single failure. These defaults and alert 
settings can be modified within the Sentry UI. The `update_task_monitor` task does nothing but allows Sentry to monitor 
the worker server for automated downtime detection.