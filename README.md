# gitlab-webhook-telegram

## What can gitlab-webhook-telegram can do for you ?

Gitlab-webhook-telegram (GWT) offers a simple app to monitore gitlab webhooks and to send message to telegram chats. It allows you to handler mutliple projects and multiple chats (only one instance of the project is needed).
GWT also implements a daemon wrapper to use start, stop and restart and easily turn this python app into a service.

## What can't GWT do for you ?

Coffee, a nuclear weapon and a large number of other things.

## How to use it 
Easy install :

1. You can install the package with pip : `pip install gitlab-webhook-telegram`
2. Create /etc/gwt folder and copy config json files from the package (/home/username/.local/lib/python/site-packages/gwt/all.json. You need to change the owner of the folder (or a least the rights) in order to have the folder accessible (read, write) to the user
3. Create a /var/log/gwt/ folder and give the required rights (read, write) to the user

You can then use the gwt command : 
 gwt start
 gwt stop
 gwt restart
 gwt test

`gwt start`: start the daemon
`gwt stop` : stop the daemon
`gwt restart` : stop and start the daemon
`gwt test` : execute main method but without starting any daemon
