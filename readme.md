# Local Project Setup

```
# Create environment config file.
cp config/.env.example config/.env

# Fill in appropriate environment values.
nano config/.env

# Install pip requirements.
pip install -r requirements.txt

# Apply migrations and sync database schema.
python manage.py migrate
```

To run the project:
```
python manage.py runserver_plus
```
To access the database:
```
python manage.py shell_plus
```
To run test suite:
```
python manage.py test
```
To run style checks and desired formatters:
```
pre-commit run --all-files
```
To add a new dependency to or update requirements, add the entry to requirements.in and run `pip-compile` to generate requirements.txt:
```
vim requirements.in  # Updating Python dependencies as needed
pip-compile --upgrade  # Generate requirements.txt with updated dependencies
```

# Project Template Setup
```
pip install pip-tools
nano requirements.in  # Choose project requirements
pip-compile --upgrade  # Generate project-specific requirements.txt with updated dependencies
nano readme.md  # replace this README with project relevant details
```

## Included Optional Features

There are a number of optional features that have been included in this sample.
The code related to each sits between comments
`# START_FEATURE feature_name` and `# END_FEATURE feature_name`.
Before using this codebase, you should chose which features you don't want to use and remove all
of the code between the tags for that feature.  Following that, you should remove all of the
`# START_FEATURE` and `# END_FEATURE` comments from the codebase.
Following that, you should run `pip-compile`.

The following is a list of tagged features in this repo:

```
elastic_beanstalk
recommended_production_security_settings
bootstrap_messages
django_social
crispy_forms
django_storages
docker
django_ses
sentry
```

The codebase also has a number of reference examples.  These are all marked with the comment:
```
# TODO: delete me; this is just a reference example
```

## Optional Settings

`MAINTENANCE_MODE`: Set this flag on a server environment to stop all user requests to the site, such as when you need to make substantial server updates or run a complex database migration.


## Deployment
Prerequisites:
- AWS CLI
```
pip install awscli
pip install awsebcli
```

#### Create a new deployment
[Set up your local AWS credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html) e.g. ~/.aws/config
Then use [eb-create-environment](https://github.com/zagaran/eb-create-environment/)
```
eb-create-environment
```
#### Update an existing deployment
```
eb deploy [ENVIRONMENT_NAME]
```
####  SSH into an existing deployment
Use [eb-ssm](https://github.com/zagaran/eb-ssm/)
```
eb-ssm [ENVIRONMENT_NAME]
```

# sample-django-app TODO

Write a setup script that does the following:

* prompts the user for a project name and replaces instances of `[PROJECT]` with that name
* prompts the user with each feature tag and removes the code between those feature tags or not
* runs pip-compile
* remakes migrations
