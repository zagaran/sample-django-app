#!/bin/bash
# START_FEATURE elastic_beanstalk
source $PYTHONPATH/activate

# START_FEATURE django_react, sass_bootstrap
npm install --production
# END_FEATURE django_react, sass_bootstrap

# START_FEATURE django_react
$(npm bin)/nwb build --no-vendor
# END_FEATURE django_react

# START_FEATURE sass_bootstrap
python manage.py compilescss
# END_FEATURE sass_bootstrap

python manage.py collectstatic --noinput --ignore *.scss
# END_FEATURE elastic_beanstalk
