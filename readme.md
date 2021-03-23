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


# Feature Descriptions


## Django-React


### Additional Setup


When using this feature, make sure to install the Node.js requirements using the manager of your choice 
(either `npm install` or `yarn install` will work) before proceeding with development.


### Special Consideration for Running


For development on localhost when using Django-React, you should run the following command in a separate terminal to
your standard `runserver` command.
    
- `nwb serve --no-vendor`

If you have configured everything correctly, you should see each command complete and notify you
that the project is ready to be viewed.


### Adding a new React component


In this paradigm, React components are compiled and injected into the standard Django template. This means we can take 
advantage of the built-in templating functionality of Django and, with a bit of elbow grease, use the power of React to
make those templates responsive.

`django-react-loader` uses the same basic pattern for any component:

1. First, ensure that the library is loaded in your template: `{% load django_react_components %}`
2. Next, ensure that you have rendered the React runtime bundle: `{% render_bundle 'runtime' %}`
   - Note that you only have to do this once per page where React components will be used. 
3. Finally, load your React component on the page. `{% react_component 'Home' id='home' %}`
    - You can add any number of props as named keywords, e.g. `{% react_component 'Home' id='home' prop1=value_from_context %}`
    - You can also choose to pass props as an object instead of individual kwargs.

### Preparing for deployment


The preferred option for deployment is to add the below compilation step to the deployment configuration rather than 
building it locally. However, if you wish to build the app locally:

- run `nwb build --no-vendor`. This will generate or replace a `webpack_bundles` folder in your `/static` folder populated with the compiled React components.


### Other Notes


- If you use `nwb serve` in your local development environment, you may see a persistent XHR error in the console -- a 
request by the app to something like `http://localhost:8000/sockjs-node/info?t=123456789`. This is normal and will 
  not appear on production or otherwise affect the function of your app. It is an artifact of the context bending we are
  doing by placing a React component outside the context of its expected Node environment.

- Note that calling `nwb build` does not remove existing compiled data from your static folder -- it may be worth deleting
`/static/webpack_bundles` before running a build for a deploy, as otherwise your package may become heavier than it
needs to be.
   - If you find that the number of files collected by `python manage.py collectstatic` continues to grow, this may be
    a sign that you should consider deleting the generated files and the `staticfiles` directory and starting with a
     fresh `python manage.py collectstatic`. This is another reason to prefer adding a compilation step to your deployment
     pipeline rather than running it locally.
     

# TODO


Write a setup script that does the following:

* prompts the user for a project name and replaces instances of `[PROJECT]` with that name
* prompts the user with each feature tag and removes the code between those feature tags or not
* runs pip-compile
* remakes migrations