# The Strain RX project.

![image](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg)
[Built with Cookiecutter Django](https://github.com/pydanny/cookiecutter-django/)


# Local install guide
You should have python 3.5.1 installed as well as Nodejs 4.4.7

1. Fork and then clone your fork.  
1. create a virtualenv and activate it
1. From the cloned directory run:  
    `pip3 install -r requirements/local.txt`
    
    `npm install`  
1. Install gulp `npm install gulp`
1. Run `gulp` (builds all static files and will watch for changes and rebuild while it is running)
1. Create a local Postgre DB (`createdb`) then change your `local.py` settings to point to your DB.  
1. Run `python manage.py migrate`.  
1. To create a superuser: `python manage.py createsuperuser`
1. Setup static files: `pyton manage.py collectstatic -link`
1. To run server: `python manage.py runserver` and visit localhost:8000


## Install ElasticSearch
THE VERSION OF ELASTICSEARCH IS >>>VERY<<< IMPORTANT Must be >5.2
1. Download ES 5.2.x and matching Kibana from https://www.elastic.co/downloads
    1. Unzip and move both to directory of your choice
1. From within ES directory run `bin/elasticsearch` - ES should now be running at http://localhost:9200
1. From within Kibana directory run `./bin/kibana plugin --install elastic/sense` to install sense plugin
1. From within Kibana directory run `./bin/kibana`
    1. You should now be able to use sense to interact with ES at http://localhost:5601/app/sense
1. In the ES directory under `/config/elasticsearch.yml` add these two lines to enable inline scripts:
    
        ```
           script.engine.groovy.inline.aggs: on
           
           script.engine.groovy.inline.search: on
        ```
        
## Common Management Commands to Init Data
1. Import all strains to ES: `python manage.py etl_strains_to_es --drop_and_rebuild --index=strain`
1. Import all strains to psql: `python manage.py import_strain_csv --csv_path=data/full_strain_db.csv`
1. Build user ratings: `python manage.py build_strain_rating_es_index --index=user_ratings --drop_and_rebuild`
1. Import all biz locations and menus to ES: `python manage.py build_bus_locations_es_index --index=business_location --drop_and_rebuild`


# Settings

Moved to [settings](http://cookiecutter-django.readthedocs.io/en/latest/settings.html).


# Basic Commands

### Setting Up Your Users

-   To create a **normal user account**, just go to Sign Up and fill out the form. Once you submit it, you’ll see a “Verify Your E-mail Address” page. Go to your console to see a simulated email verification message. Copy the link into your browser. Now the user’s email should be verified and ready to go.
-   To create an **superuser account**, use this command:

        `python manage.py createsuperuser`

For convenience, you can keep your normal user logged in on Chrome and your superuser logged in on Firefox (or similar), so that you can see how the site behaves for both kinds of users.

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:
    ```
        coverage run manage.py test
        coverage html
        open htmlcov/index.html
    ```

#### Running tests with py.test

    `py.test`

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](http://cookiecutter-django.readthedocs.io/en/latest/live-reloading-and-sass-compilation.html).


# Deployment

The following details how to deploy this application.
### TODO





