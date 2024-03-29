# Updating the Template Repository

This repo is autogenerated from [zagaran/django-template](https://github.com/zagaran/django-template/)

**Do not edit this repo manually.**

To update this repo, make a branch on django-template and then run the following commands:

```bash
pip install cookiecutter
# Note: this python scripts assumes your branch names on both `django-template` and `sample-django-app` are the same
echo 'import os; import subprocess; from cookiecutter.main import cookiecutter; checkout = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip(); project_slug = os.path.basename(os.getcwd()); cookiecutter("https://github.com/zagaran/django-template", checkout=checkout, extra_context={"project_slug": project_slug, "feature_annotations": "on"}, overwrite_if_exists=True, no_input=True, output_dir="..")' | python3
pip install pip-tools
pip-compile requirements.in --upgrade
pip-compile requirements-dev.in --upgrade
rm package-lock.json
rm -rI node_modules
npm install
```


## Pull requests

**All changes to this repo should have two pull requests: one on django-template and one on sample-django-app**

This repo exists as a legible example of the app generated by the template repository. Due to `cookiecutter` formatting,
the source repository is difficult to read on its own. When bug-fixing or adding features, the following process will ensure
feature parity between repos and a smoother overall development cycle.

1. Create a new branch on the `django-template` repo, make your changes there, and add any template tags needed for 
`cookiecutter` feature selection. This code is already present in many places throughout the template repo; 
look for `{%- if cookiecutter.feature_annotations == "on" -%}` for examples.
   1. If you are adding a new feature, make sure that you add the relevant feature tag to `hooks/post_gen_project.py` and
   that you have added a description of the feature to `readme.md`. 
   2. If you are updating an existing feature in a meaningful way (i.e. a breaking or significant change to its 
   usage paradigm) you should update the relevant part of `readme.md`.
   3. The dashes contained in the existing template tags are not mistakes; they are added intentionally to preserve 
   whitespace formatting during the `cookiecutter` project creation process. If you add a new feature, you should emulate
   the style of existing template tags.
2. Make a branch on the `sample-django-app` repository (this repository) with the same branch name.  Run the above command.
3. Ensure that the code runs propersly on `sample-django-app` and is styled properly.  In particular, check the following URLS:
    1. http://localhost:8000/
    2. http://localhost:8000/django-react/
5. Make a PR on the `django-template` repo.
6. Make a PR on the `sample-django`app` repo (this repo).
