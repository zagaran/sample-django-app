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
# Elastic Beanstalk

The following Python packages are useful tools for interacting with AWS and Elastic Beanstalk.
Due to dependency conflicts, these should not be installed in your project's regular virtual environment,
and should instead either be installed globally or in a separate virtual environment that runs them:

```bash
pip install awscli  # For interacting with general AWS services (note, this package often has conflicts with its botocore dependency)
pip install awsebcli  # For interacting with Elastic Beanstalk (note, this package often has conflicts with its botocore dependency)
pip install eb-create-environment  # For automating the creation of Elastic Beanstalk applications
pip install eb-ssm  # For Elastic Beanstalk SSH functionality without requiring shared private keys
```

## Creating a new environment

To do create a new Elastic Beanstalk environment, modify the contents of [.elasticbeanstalk/eb_create_environment.yml]([.elasticbeanstalk/eb_create_environment.yml]) and run `eb-create-environment -c .elasticbeanstalk/eb_create_environment.yml`.

See the docs for [eb-create-environment](https://github.com/zagaran/eb-create-environment/) for more details.

Following that, deploy your code to the environment (see below).

## Deploying code

To deploy new versions of your code to your environment, run `eb deploy <environment_name>` using the EB CLI to deploy your code to that environment.

See the [eb-cli](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html) docs on general command line usage of Elastic Beanstalk.

## SSH

To SSH into an Elastic Beanstalk Environment, use [eb-ssm](https://github.com/zagaran/eb-ssm).