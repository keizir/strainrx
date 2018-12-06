#!/bin/bash

DEPLOY_ENV="$DJANGO_SETTINGS_MODULE"

while true; do
    read -p "Deploy to ${DEPLOY_ENV}?" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit;;
        * ) echo "Yes or No please.";;
    esac
done
echo "deploying ${DEPLOY_ENV} ${DEPLOY_BRANCH}"


# pull changes, install dependencies, and build assets
git fetch origin && git reset --hard origin/${DEPLOY_BRANCH}
# silence "already satisfied" warnings"

pip install -r requirements/production.txt 1> >(grep -v 'Requirement already satisfied' 1>&2)

# install front end dependencies
npm install
gulp prod

# migrate pending database migrations and collect all static files
echo "running migrations..."
python manage.py migrate
echo "running collectstatic..."
python manage.py collectstatic --noinput --verbosity=0

#restart gunicorn
echo "Restarting gunicorn..."
if pgrep "gunicorn" > /dev/null
then
    sudo systemctl stop gunicorn_srx_web.service
fi
sudo systemctl enable gunicorn_srx_web.service
sudo systemctl restart gunicorn_srx_web.service

echo "deploy complete"
