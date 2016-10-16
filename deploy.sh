#!/bin/bash

# go to project directory
cd /srv/www/web

# activate python environment
source srx_env/bin/activate

DEPLOY_ENV="$DJANGO_SETTINGS_MODULE"
DEPLOY_BRANCH="master"


while true; do
    read -p "Deploy to ${DEPLOY_ENV}?" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Yes or No please.";;
    esac
done
echo "deploying ${DEPLOY_ENV}"


# pull changes, install dependencies, and build assets
git fetch origin && git reset --hard origin/${DEPLOY_BRANCH}
# silence "already satisfied" warnings"

pip install -r requirements/production.txt 1> >(grep -v 'Requirement already satisfied' 1>&2)

# install front end dependencies
npm install
gulp prod

# migrate pending database migrations and collect all static files
python manage.py migrate
python manage.py collectstatic --noinput --verbosity=0

#restart gunicorn
echo "Restarting gunicorn"
if pgrep "gunicorn" > /dev/null
then
    stop srx-gunicorn
fi
start srx-gunicorn

echo "deploy complete"