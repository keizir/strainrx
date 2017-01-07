# Ansible Setup

## General
* [Ansible](http://docs.ansible.com/ansible/) is indempotent so feel free to run commands again and again
* Django env vars are in encrypted file `/env_vars/django_<env>.yml` so you can put secrets in there and commit to repo
	* See [http://docs.ansible.com/ansible/playbooks_vault.html](http://docs.ansible.com/ansible/playbooks_vault.html) for how to edit / view the file 

## Add Ansible Config to Your Project
1. Customize all vars in files for your project:
	* `env_vars` (encrypt all `django_<env>` files)
	* `production` `stage`

## Setting up Ubuntu 16.04 from scratch
### Manual Steps
1. Create new Ubuntu 16.04 server on AWS, saving .pem file
1. SSH to instance
	2. On initial connection using pem file (remember to `chmod 600` your .pem locally or you'll get an error) add your SSH key to authorized_keys for ubuntu user
	2. Install python 2.7 (required by Ansible for now) and other dependencies 
		3. `sudo apt-get update` 
		3. `sudo apt-get install python-dev python-pip letsencrypt`
	3. Create users for any developers who will need to connect via Creating a New User steps below and add their public keys
	4. Create SSL cert with Let's Encrypt and Certbot
		5. see current instructions at [https://certbot.eff.org/#ubuntuxenial-nginx](https://certbot.eff.org/#ubuntuxenial-nginx)
		6. Run `sudo letsencrypt certonly --standalone -d domain.com -d www.domain.com` and so long as that domain is publicly accessible you should be OK
	7. Install Nodejs
		8. As `root` follow steps to install node LTS 4.2.6 via NVM at [https://github.com/creationix/nvm#install-script](https://github.com/creationix/nvm#install-script) so we can run FE build tasks
		9. `source ~/.bashrc`
		10. `nvm install 6.9.4 && nvm use 6.9.4 && nvm alias default node`
    1. Create virtualenv
        1. `pip3 install virtualenv virtualenvwrapper`
        2. `mkvirtualenv -p python3 <application name>`

### Run with Ansible
3. Run Playbook: `ansible-playbook -i <env> site.yml --ask-vault-pass` (where env = stage, prod, etc to set up various environments)
	4. On very first run you'll get an error on git step - on server copy the SSH key for `root` and add it as deploy key in git repo - then re-run ansible command above

### Creating a New User 
1. (on local) Copy your SSH key. Usually in `~/.ssh/id_rsa.pub`
1. (on server) Create user: `sudo adduser <user>`
2. Note password if this will be a shared user (make it strong)
2. Add user to sudo group: `sudo adduser <user> sudo`
3. Switch to new user: `sudo su - <user>`
4. Add your SSH keys:
	5. `mkdir .ssh`
	6. `vi ~/.ssh/authorized_keys`
	7. Paste in your SSH key for your local machine 
8. Adjust permissions on keys and ensure new user owns their home directory: 
	
	```
	chmod 400 /home/<user>/.ssh/authorized_keys
	chown <user>:<user> /home/<user> -R
	```
9. Disconnect from server and test that you can connect with new user via `ssh <user>@<server>`


## Useful Commands
* `ansible-vault encrypt <path to file(s)>` and `ansible-value decrypt <path to file(s)>` for working on encrypted files