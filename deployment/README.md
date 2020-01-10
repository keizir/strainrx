### Instructions how to setup a server to run a django app  

1. `chmod 400 ~/.ssh/strains-stage.pem` 
2. SSH to the stage server `ssh -i ~/.ssh/strains-stage.pem ubuntu@54.70.213.66`
  
3. Then run  
`sudo apt-get update`  
`sudo apt-get upgrade`  
`sudo apt-get install git`  
`sudo apt-get install python3-pip`  
`sudo pip3 install --upgrade pip`  
`sudo apt-get install python-dev`  
`sudo apt-get install build-essential`  
`sudo apt-get install libpq-dev`  
`sudo apt-get install postgresql postgresql-contrib`  
`sudo pip3 install gitsome`  
`sudo pip3 install sendgrid`  
`sudo apt-get install nodejs`  
`sudo apt-get install npm`  
  
4. Under **/home/ubuntu** create directory **app**.  
`cd /home/ubuntu/app`  

5. Clone the latest code from github. You will require your github credentials to perform this action.  
`git clone https://github.com/straintechinc/web.git`  

6. After cloning `cd web` and run  
`pip install -r requirements/stage.txt`
  
7. Change `export DJANGO_SETTINGS_MODULE=config.settings.stage`  
8. Run `npm install`  
9. `python3 manage.py migrate`
10. `python3 manage.py runserver`