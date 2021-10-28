# Gitlab Deploy Keys

We need to generate an SSH private/public key pair so that fabric can
checkout and pull files to deploy on the servers.  
See `packages/git/__init__.py` for more information on how this works

## Generate Key

* https://docs.gitlab.com/ee/ssh/README.html
* Save to `/Users/chris/id_rsa_deploy`

```
cd ~
ssh-keygen -t rsa -b 2048 -C "{{project}}"
```

* This will create two files in the directory specified above
  * `/Users/chris/id_rsa_deploy`
  * `/Users/chris/id_rsa_deploy.pub`

## Copy into Project Repository fabric folders

* Fabric folder normally is `~/Project/bin/fabfile`
* Copy files to where fabric will be looking for these
	* `cp ~/id_rsa_deploy ~/Project/bin/fabfile/environments/git`
	* `cp ~/id_rsa_deploy.pub ~/Project/bin/fabfile/environments/git`

## Copy/Paste the public key to the Gitlab project

* Go to https://gitlab.com
  * Specifically, a project directory that looks like
  * https://gitlab.com/group/web
* Then go to Settings > Repository (left side)
* Go to Deploy Keys, click on Expand
  * Title: {Project} Deploy Key
  * Key: Open up `id_rsa_deploy.pub` (in Atom or text editor)
  * Key: Paste contents into textarea
  * Do not check "Grant write permissions ... " (default)
  * Click on Add Key
