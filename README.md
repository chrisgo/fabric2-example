# Fabric2 Example

Example of how you can organize a set of **fabric2** scripts.  Mostly this is just
how I organized my fabric build and release process and sharing to possibly help
other folks get started.

Note: You should use
[Ansible](https://www.ansible.com/) +
[Ansistrano](https://github.com/ansistrano/deploy)
or
[Terraform](https://www.terraform.io)
if you need more support.

We want to use **fabric2** to be able to handle the deprecation of Python 2.x.
It will get harder and harder to install python 2.x into newer systems so we
need to upgrade to be able to use Python 3.x that is now the default.  

*Old fabric 1.x example is here https://github.com/chrisgo/fabric-example*

* Fabric: http://fabfile.org
* Fabric Docs: https://docs.fabfile.org/en/2.6/

This example using **Python 3.x** 100%.  We are **NOT** doing any of the upgrades as
described in the documentation.  

* NOT "side-grading"
* NOT running 2 version of fabric simultaneously
* NOT using config objects from v1

On a Mac, you will need to run `source ~/venv-fabric2/bin/activate` on
each terminal you start, see [Mac Setup](#mac-setup)

---

Mostly I deal with a standard LEMP stack (Linux, Nginx, MySQL and PHP-fpm) on Debian
so please adapt for your own use.  The original goal was to deal with Vagrant and
Linode or Amazon AWS but I ended up just implementing Vagrant and DigitalOcean as
"deployment targets".  Currently, this example is for Debian 10 (bullseye)

These scripts should be run in the directory where the fabfile directory lives.  
*If you do an ls, you should see the directory called "fabfile"*

## Goals

1. Build servers quickly based on:

    * Environments => developer, dev, qa, stage, production
    * Roles        => www, database, resque, balance

1. Normalize all the different cloud providers

    * Providers    => digitalocean, ec2, linode, vagrant

1. Be able to customize each project while sharing core fabric files

    * Core: __init__.py, roles/, packages/ and providers/ folders
    * Per project: environments/ folder

## Usage

```
fab <environment> <branch> release    # Release code
fab <environment> <role> <task>       # Builds servers

Examples:

fab dev master release                # standard release to dev
fab local --user=chris www release    # standard release to chris (developer)

fab dev www normalize                 # step 1 (normalize providers + basic)
fab dev www server                    # step 2 (server role specific)
fab dev www project                   # step 3 (project specific)
```

## New Projects

1. Check project/__init__.py to make sure all project-specific settings are correct
1. Check `environments/*.py` to make sure all the servers are correct

## New Hosts (Servers)

For new servers (new file environments), we need to do some setup:

* Create the appropriate settings for the system, usually this is for a new developer
  or a new server starting from scratch
* Make sure to note down the provider (Vagrant, Linode, etc.)
* Make sure this <environment> is unique across everything ever created for this project
* The fabric system will pick up the settings for that environment

Run through steps 1-3

1. fab <environment> <role> normalize
  * Normalizes each provider (Vagrant, Linode, etc)
  * Installs basic setup for ALL servers
2. fab <environment> <role> server
  * Installs more software by server role
3. fab <environment> <role> project
  * Installs project-specific software by server role
  * Also initializes the project on the server by server role

For normal releases to an environment (for example: dev), run

```
fab dev www release
```

and for PRODUCTION, run it with a group argument

```
fab production www release
```

### Mac Setup

The easiest way to get your Mac setup is to use `homebrew` and `venv`.  

* Install zsh https://github.com/ohmyzsh/ohmyzsh
  * `sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"`
  * In theory, this is recommended on MacOS as it adds some features on top of the
    default `bash` shell
* Install `homebrew` https://brew.sh/
* Install python3 using Homebrew
  * `brew install python` - this should install python 3.9.x (3.9.7)
* Use python3 to create a venv in a folder **outside** of the repository
  * https://towardsdatascience.com/virtual-environments-104c62d48c54
  * Note: `venv` needs to be activated on **each** terminal you start
  * To create your python3 virtual environment to run fabric2, run the following:
  * `python3 -m venv ~/venv-fabric2` => creates this in your home directory
  * `source ~/venv-fabric2/bin/activate` => activates in current terminal
  * `python -V` => should say Python 3.9.x
* Install fabric
  * On the same terminal as above
  * `pip install fabric` => installs python3.x fab in `~/venv-fabric2/bin`
  * See bin/fabfile/README.md for other information

## TODO

* [x] Create custom (own own) Connection that extends fabric2 Connection
  * This allows us to create more functions without passing `c` all over
* [x] Move custom Connection object into core/connection.py
* [x] Move packages/util.py into here into core/util.py
* [x] Replace string manipulation with python f-strings
  * https://realpython.com/python-f-strings/
  * https://stackoverflow.com/questions/42097052/can-i-import-pythons-3-6s-formatted-string-literals-f-strings-into-older-3-x (see `pip install future-fstrings` above)
* [ ] Make the main __init__.py script have less code by moving code into core/*
  * Global `config` object hard to pass into a class outside main __init__.py
* [ ] Dashes for task names vs underscore for function name
  * http://docs.pyinvoke.org/en/stable/concepts/namespaces.html#dashes-vs-underscores

---

## Fabric2 Changes

* (1) Fabric2 is now broken into 3 distinct libraries
  * Fabric: https://www.fabfile.org/
  * Invoke: http://www.pyinvoke.org/
  * Patchwork: https://fabric-patchwork.readthedocs.io/en/latest/index.html
* (2) Might have to install more python libraries using pip (may need sudo)
  * `pip install invoke`
  * `pip install patchwork`
  * `pip install colorama`
  * **IMPORTANT** If by installing one of the libraries above, it ends up
    install fabric2 into you  `fab` command (if you type `fab --version`,
    it shows Fabric 2.6.x), you can downgrade back to original fabric by typing
    `pip install 'fabric<2.0'` or a specific version like
    `pip install fabric==1.14.1`.  Then type `fab --version` again and it should
    show that you are back to version 1.14.1
* (3) Fabtools no longer work
  * https://github.com/fabtools/fabtools
  * We are porting some of these over inside `core/fatools/*`
* (4) no more import *
  * `from environments import *` no longer works
