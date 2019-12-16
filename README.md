# Gitlab-webhook-telegram

## What can GWT do for you ?

Gwt is a simple python server triggered by gitlab webhooks which trigger messages on telegram via a bot.

Some functionnalities : 
 * bind multiple projects to multiple chats
 * display messages for every type of gitlab webhook
 * choose message length with verbosity per chat and per project
 * configure nearly all the bot by interaging with it on telegram (optional)
 * easliy turn the app into a service

## Installation

### 0) Prepare

You will need a server with python3 and pip.

### 1) Get a telegram bot

First things first, you need a telegram bot. To get one, you need to interact with @BotFather on telegram. Please refer to https://core.telegram.org/bots for the explicit procedure. You should et a token (like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`) and we will refer with `<token>` for the following.

### 2) Clone the repository

You can clone the git repository with 

```
git clone https://github.com/nanoy42/gitlab-webhook-telegram.git
```

Then you need to install the required python modules. The list is in requirements.txt and you can install all requirements with the command :

```
pip3 install -r requirements.txt
```

Note : If you want you can use a virtual environment, but you will have to tweak the rest of tutorial to get it work.

### 3) Configure the app

There are 3 files to edit in order to get the bot working.

Note : If you choose to use `configure-by-telegram` option, only one file need to be edited

First copy example configuration files where the app is installed 

```
cp config.json.example config.json
cp verified_chats.json.example verified_chats.json
cp chats_projects.json.example chats_projects.json
```

Note : if you want to have the configuration files elsewhere (in `/etc/gwt/` for example), please refer to the FAQ.

#### 3.1) config.json

This is the main configuration file.

It looks like 
```json
{
    "configure-by-telegram": true,
    "port": 8080,
    "telegram-token": "",
    "passphrase": "Here we go !",
    "gitlab-projects": [],
    "log-file": "./gwt.log",
    "log-level": "debug"
}
```
| Parameter                 | Type                                      | Default value    | Description                                                                                                                    |
|---------------------------|-------------------------------------------|------------------|--------------------------------------------------------------------------------------------------------------------------------|
| `configure-by-telegram`   | boolean (`true` or `false`)               | `true`           | If `true`, it will possible to verify chats, add and remove projects, change verbosity of projects directly in telegram chats. |
| `port`                    | integer (between 0 and 65535)             | 8080             | The device port on which the web server should run.                                                                            |
| `telegram-token`          | string                                    | `""`             | The value of the telegram bot token.                                                                                           |
| `passphrase`              | string                                    | `"Here we go !"` | A passphrase to verify chats when `configure-by-telegram` is set to `true`.                                                    | 
| `gitlab-projects`         | array (see below)                         | `[]`             | An array of configured projects. See below.                                                                                    |
| `log-file`                | string                                    | `"./gwt.log"`    | Absolute or relative path to the log file. Make sure the process has the right tro write there.                                |
| `log-level`               | string                                    | `"warning"`      | The log level.                                                                                                                 |

The array of `gitlab-projects` should contain name and token for each project :

| Parameter | Type   | Description                                                           |
|-----------|--------|-----------------------------------------------------------------------|
| `name`    | string | Pretty name of project                                                |
| `token`   | string | Token of project. It sould be the same as on the gitlab webhook page. |

The log level should be picked among :
* info
* debug
* warning
* error
* critical

More information on the log levels : https://docs.python.org/fr/3/howto/logging.html

A working example :

```json
{
    "configure-by-telegram": true,
    "port": 8080,
    "telegram-token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    "passphrase": "BCX2ipcGv5wCorPUWhTi9SXfWK6gz7",
    "gitlab-projects": [
        {
            "name": "My awesome project",
            "token": "this is a secret token"
        },
        {
            "name": "Another project",
            "token": "G4oJnAm9ljWksgfjGTnUcUguv6WvkF"
        }
    ],
    "log-file": "/var/log/gwt/gwt.log",
    "log-level": "warn"
}
```

Note : The log-file parameter is ignored when the server is launched with the `python3 manage.py test` command and the logs are printed to the console.

#### 3.2) verified_chats.json

If you use `configure-by-telegram`, the bot will propose you to verify the chat on the `/start` command (you will have to send the passphrase on the chat) and will write the verified_chats.json file. If you don't want to use `configure-by-telegram` or don't want to send the passphrase you should manually add the chat ip in the verified_chats.json file. 

The file is composed by a array of integers, which represent telegram chats identifier.

How to get this identifier : the bot will display the chat id if the chat is not verified (wether `configure-by-telegram` is se tot `true` or `false`).

You can also use https://api.telegram.org/bot<YourBOTToken>/getUpdates.

A "working" example :

```json
[1, -234, 10]
```

#### 3.3) chats_projects.json

This file allows to keep trak of relations betweens chats and projects.

You could see config.json has storing projects, verified_chats.json the chats and chats_projects.json the relations between the two.

The format of this file is the following : 
```json
{
    "token": {
        "chat_id": verbosity,
        "chat_id2": verbosity2
    }
}
```

Messages for the project associated to token will be sent to all chats in the dictionnary with the associated verbosity.

The tokens and the chat ids should be in `config.json` and `verified_chats.json` respectively.

A working example :

```json
{
    "this is a secret token": {
        "1": 3
    },
    "G4oJnAm9ljWksgfjGTnUcUguv6WvkF": {
        "-234": 1,
        "1": 2
    }
}
```

A webhook from the "My awesome project" project will be sent to the chat with id 1 with a verbosity of 3.

A webohhom from the "Another project" project will be sent to the chats with id -234 and 1 with verbosities 1 and 2 respectively.

Even if the chat with id 10 is in the `verified_chats.json` file, no message will reach it.

### 4) Test the app

You can start the server with the 

```
python3 main.py test
```

You can then test the bot by interaging with i on messenger and use the test button on the gitlab interface.

### 5) Make it a service

The `main.py` script allows 5 commands : `start`, `restart`, `stop`, `test` and `help`.

The `help` command displays an help message.

The `test` command runs the server but ends with an intureption (ctrl-c) or the user`s session end. Also, logs are printed in console and not in file.

The `start`, `restart` and `stop` commands allows to use the a daemonized script. You can easily use those commands to make gwt a service to start when the server boots.

## How to use the bot

The behavior of the bot depends on the value of `configure-by-telegram`.

### configure-by-telegram is false

In this case, the bot will react to three commands : `/start`, `/help` and `/listProjects`.

Note : the bot will trivially react to other commands with the following message : If you want to configure the bot with telegram, please set the 'configure-by-telegram' option to true in the settings.

| Command         | Usage                                                                                                                                                                     |
|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/start`        | Begin point of the bot. In this case, it basically dislays the id of the current chat.                                                                                    |
| `/help`         | Will display the list of available commands and the version of the bot.                                                                                                   |
| `/listProjects` | Will display the configured projects for this chat and the verbosity of each, reprensented by an integer (from 0 to 3). The higher the integer, the verbosier the bot is. | 

### configure-by-telegram is true

In this case, the bot will react to three commands : `/start`, `/help`, `/listProjects`, `addProject`, `removeProject` and `changeVerbosity`.

| Command            | Usage                                                                                                                                                                     |
|--------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/start`           | Begin point of the bot. In this case, it displays the chat id and propose to verify chat by sending the passphrase.                                                       |
| `/help`            | Will display the list of available commands and the version of the bot.                                                                                                   |
| `/listProjects`    | Will display the configured projects for this chat and the verbosity of each, reprensented by an integer (from 0 to 3). The higher the integer, the verbosier the bot is. |
| `/addProject`      | Will display an interactive keyboard to choose a non-configured project to add to the current chat. The project will be added with the maximal verbosity (3).             |
| `/removeProject`   | Will display an interactive keyboard to choose a configured project and delete it from the table.                                                                         |
| `/changeVerbosity` | Will display an interactive keyboard to choose a configured project and change its verbosity.                                                                             |

## Under the hood

How does the app works.

When receiving a post request from Gitlab, it will retrieve the token and verify that the token is in the `config.json` file. If it is not, it will log an error and if it is it will retrieve the type of the hook in the following list :

* PUSH
* TAG
* ISSUE
* CONFIDENTIAL_ISSUE
* NOTE
* CONFIDENTIAL_NOTE
* MR
* JOB
* WIKI
* PIPELINE

Then it will call the appropriate handler with the POST parameters. Each handler will then print message accordinglyot the chat verbosity and send it.

The bot also listen for messages and commands (messages with `/`) and react accordingly to write configuration files.


## FAQ

### Any python framework for the server ?
No it is written only using requests.

### Can I use this chat for a group ? For a single user ?

Yes you can do it for both. 

For a single user to have to search the bot name and start chating with it.

For a group, you have to invite him on the group.

### I want to put the configuration files elsewhere

If you want to have the configuration files in another directory (say `/etc/gwt/`), it is possible to do so by setting the `GWT_DIR` environment variable (using `export` command for instance) . It sould be an abstract path to a readable-writable directory (the script writes ine the configuration files). You have to put the final / :

```
export GWT_DIR=/etc/gwt/
```

Note : you can use a relative path here but this is strongly discouraged.

### Verbosities ?

There are 4 levels of verbosity, described below :

| Level | Description                                                                                                                        |
|-------|------------------------------------------------------------------------------------------------------------------------------------|
| 0     | Print all except issues descriptions, assignees, due dates, labels, commit messages and URLs and reduce commit messages to 1 line. |
| 1     | Print all except issues descriptions, assignees, due dates and labels and reduce commit messages to 1 line.                        |
| 2     | Print all but issues descriptions and reduce commit messages to 1 line.                                                            |
| 3     | Print all.                                                                                                                         |


### Can I configure the projects and turn `configure-by-telegram` afterwards ?

Yes. It is even recommended.

### How do I block certain types of handlers ?

You cannot block on the app side, but you can select what webhooks are active in the gitlab pannel.
