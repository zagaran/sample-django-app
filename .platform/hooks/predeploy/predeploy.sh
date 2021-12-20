# START_FEATURE elastic_beanstalk
#!/bin/bash
source $PYTHONPATH/activate

# START_FEATURE django_react
npm install -G nwb
npm install
./node_modules/.bin/nwb build --no-vendor
# END_FEATURE django_react

# START_FEATURE sass_bootstrap
python manage.py compilescss
# END_FEATURE sass_bootstrap

python manage.py collectstatic --noinput --ignore *.scss
# END_FEATURE elastic_beanstalk
