# The Strain RX project

### Local install guide
1. Fork and then clone your fork.  
2. From the cloned directory run:  
`pip3 install -r requirements/local.txt`  
`npm install`  
3. Create a local Postgre DB then change you `local.py` settings to point to your DB.  
4. Run `python manage.py migrate`.  
5. Run `gulp`.  
6. In parallel run `python manage.py createsuperuser` and `python manage.py runserver`.  
7. Ping http://127.0.0.1:8000/.  

### Sending emails  
1. Install `pip install sendgrid`  
