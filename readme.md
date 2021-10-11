# Project Template and Optional Features

This project was created using https://github.com/zagaran/django-template

See the readme on [django-template](https://github.com/zagaran/django-template) for:
* Instructions on starting your own project
* An explanation of included features.

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
To run the test suite:
```
python manage.py test
```
To get a test coverage report:
```
coverage run --source='.' manage.py test; coverage report
```
To add a new dependency to or update requirements, add the entry to requirements.in and run `pip-compile` to generate requirements.txt:
```
vim requirements.in  # Updating Python dependencies as needed
pip-compile --upgrade  # Generate requirements.txt with updated dependencies
```
