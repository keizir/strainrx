# Running web for Development

## Mac OSX

### Homebrew, python3, postgres, gettext (skip as necessary if you already have any of these installed)

1. Install [Homebrew](http://brew.sh/) - we'll use this to easily install some other dependencies

1. Install the latest 3.5.X release of python `brew install python3`

1. Install Postgres (9.5+) `brew install postgresql`

1. Install GNU gettext (used in Django's i18n library) `brew install gettext`

    1. Then symlink gettext so django can find it `brew link gettext --force`
   
    
### Install Node.js (for frontend builds)

Install NVM (node version manager)
Instructions at: [https://github.com/creationix/nvm](https://github.com/creationix/nvm)

After install:

```
source ~/.bashrc
nvm install 4.5.0
nvm use 4.5.0
nvm alias default node
```


### Virtualenv / Virtualenvwrapper Setup

1. Install: `pip3 install virtualenv virtualenvwrapper`

1. add the following to ~/.bashrc (ubuntu) or ~/.bash_profile (osx)

	```
	export WORKON_HOME=$HOME/.virtualenvs
	source /usr/local/bin/virtualenvwrapper.sh
	```

2. Reload Bash Profile

	1. Ubuntu: `source ~/.bashrc`
	2. OSX: `source ~/.bash_profile`

3. Make Virtualenv
    1. find your python3 path: `which python3`

	```
	mkvirtualenv --python=<path to python3> web
	workon web
	```
4. If that works you should see `(web)` prepending your bash prompt which indicates you are in the web virutalenv
	
	
## Running the project Locally

1. After cloning the repo locally / running cookiecutter go to the root project dir (and ensure you're inside your python virtualenv)

1. install project python dependencies `pip3 install -r requirements/local.txt`

1. install project node dependencies `npm install`

1. create db `createdb web`

1. populate db `python manage.py migrate`

1. do initial frontend build, continue to watch files for changes `gulp`


## Pycharm setup

1. to get python to be aware of your projects files and give you nice autocomplete, be able to run server from pycharm, etc

1. Pycharm > preferences > project > project interpreter > then select your virtualenv from the drop down

1. Now find the "select run / debug config" drop down menu just to the left of the run (play) and debug (bug) buttons on very top icon row of pycharm
    1. Select edit configurations
    1. In the menu hit + to add new django server, name it your project slug name
    1. specify localhost as the host then select the python interpreter (same as we set previously) and set project root folder
    1. You should now be able to hit "run" button next to config menu and run the server from pycharm
    
    