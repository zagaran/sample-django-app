This repo is autogenerated from https://github.com/zagaran/django-template/

To update this repo, run the following commands:

```
pip install cookiecutter
# Optionally replace `branch = None` with a particular branch name
echo 'branch = None; from cookiecutter.main import cookiecutter; cookiecutter("https://github.com/zagaran/django-template", checkout=branch, extra_context={"project_slug": "sample_django_app", "feature_annotations": "on"}, overwrite_if_exists=True, no_input=True, output_dir="..")' | python3
pip-compile --upgrade
rm package-lock.json
rm -r node-modules
npm install 
```