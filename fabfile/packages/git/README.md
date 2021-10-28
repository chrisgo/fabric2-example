Redmine Git Hosting Deploy Keys
====

For use with https://github.com/jbox-web/redmine_git_hosting

To create deployment keys for automated git checkouts

* Create new SSH keypair

		cd ~
		ssh-keygen -t rsa -f ~/id_rsa_deploy
    
* Copy files to project fabfile
	* cp ~/id_rsa_deploy ~/Project/bin/fabfile/project/git
	* cp ~/id_rsa_deploy.pub ~/Project/bin/fabfile/project/git

* Go to Redmine > Project > Settings > Repository
* Go to the repository line and click on  `Edit` 
	* This is usually called repositories/[project].git
* Under Deployment Credentials, click `Add Deployment Credential`
* Add Deployment Credential 
	* Select Deployment Key: (default) Create new key (below)
	* Permissions: (default) RW+
	* Identifier: (default) [Project] Deploy Key 1
	* Delete key when unused? (default)
	* Key: (copy/paste contents from `id_rsa_deploy.pub` above) 
	* Click `Save`

    

