# zds-user-map

A map for [Zeste de Savoir](https://zestedesavoir.com/)'s users! See [the related topic](https://zestedesavoir.com/forums/sujet/9260/une-carte-des-membres-de-zeste-de-savoir/) for more information (in french).

## Install notes

The goal of this section is to give an overview of what work is required to host this. It's really not much, don't worry.

The bot will need to be able to push to Git, that means a `git push` command should not require any authentication. The best way for this is to create [a personal access token](https://github.com/settings/tokens/new). It should have the `repo:public_repo` to be capable of pushing to the corresponding repository (it will also be capable of pushing to every other public repo you have the rights to, so beware).

The next step is to clone the repository. Once cloned, the origin remote URL should be modified to allow no-auth push: `git remote set-url origin https://<USERNAME>:<PERSONAL_ACCESS_TOKEN>@github.com/tleb/zds-user-map`. Now might be a good time to make sure Git knows your email address and name, which are required to create a commit. Use `git config --global user.email "foo"` and `git config --global user.name "bar"` if necessary.

Next step is running the script. It requires Python 3, pip and a few packages (the main one being requests and PyYAML). I would recommend using virtualenv or a wrapper around it (pew is one example). Assuming Python 3 and pip are installed, run the following:

```
$ # start by installing virtualenv
$ # it might require adding something to your PATH environment variable
$ python3 -m pip install virtualenv
$ virtualenv venv
$ # this assumes the bash shell but activate.zsh, activate.fish and others exist too
$ source venv/bin/activate
$ # using the local pip, we install the project's dependencies
$ pip install -r requirements.txt
```

The project will require a config file named `config.yml`. A good starting point for one is `config.default.yml`. `client_id` and `client_secret` need to be set correctly.

The next step is to acquire a refresh token from the ZdS API. The bot needs an access token to communicate with the API. There are two ways to obtain one: using the username & password combo or using the refresh token. The first refresh token needs to be acquired using the username & password. This is done through the `python main.py 0` command. Once this is done, the bot is ready to run. `python main.py 1` scans every received messages and creates the output file from those (but does not answer) and `python main.py 2` is the command that monitors unread messages and answers to those.
