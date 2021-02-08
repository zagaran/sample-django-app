# Local Project Setup

```
pip install -r requirements.txt
cp config/.env.example config/.env
nano config/.env  # Fill in missing env vars
python manage.py migrate
```


To run the project, use `python manage.py runserver_plus`

To access the database, use `python manage.py shell_plus`

# Features

There are a number of optional features that have been included in this sample.
The code related to each sits between comments
`# START_FEATURE feature_name` and `# END_FEATURE feature_name`.
Before using this codebase, you should chose which features you don't want to use and remove all
of the code between the tags for that feature.  Following that, you should remove all of the
`# START_FEATURE` and `# END_FEATURE` comments from the codebase.
Following that, you should run `pip-compile`.

The following is a list of tagged features in this repo:

```
bootstrap_messages
django_social
crispy_forms
django_react
debug_toolbar
sentry
```

The codebase also has a number of reference examples.  These are all marked with the comment:
```
# TODO: delete me; this is just a reference example
```

# TODO


Write a setup script that does the following:

* prompts the user for a project name and replaces instances of `[PROJECT]` with that name
* prompts the user with each feature tag and removes the code between those feature tags or not
* runs pip-compile
* remakes migrations