"""
Gitlab-webhook-telegram

Usage:
    main.py start
    main.py stop
    main.py restart
    main.py test

Options:
    -v --version    Show version
    -h --help       Display this screen
"""
import sys
import json
import telegram
import logging
import socketserver
from gwt import handlers
import os
import time

from http.server import BaseHTTPRequestHandler
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from gwt.daemon import Daemon
from docopt import docopt
from logging.handlers import RotatingFileHandler

"""
Here comes constant definitions
"""
MODE_NONE = 0
MODE_ADD_PROJECT = 1
MODE_REMOVE_PROJECT = 2

PUSH = "Push Hook"
TAG = "Tag Push Hook"
ISSUE = "Issue Hook"
CONFIDENTIAL_ISSUE = "Confidential Issue Hook"
NOTE = "Note Hook"
CONFIDENTIAL_NOTE = "Confidential Note Hook"
MR = "Merge Request Hook"
JOB = "Job Hook"
WIKI = "Wiki Page Hook"
PIPELINE = "Pipeline Hook"

HANDLERS = {
    PUSH: handlers.push_handler,
    TAG: handlers.tag_handler,
    ISSUE: handlers.issue_handler,
    CONFIDENTIAL_ISSUE: handlers.issue_handler,
    NOTE: handlers.note_handler,
    CONFIDENTIAL_NOTE: handlers.note_handler,
    MR: handlers.merge_request_handler,
    JOB: handlers.job_event_handler,
    WIKI: handlers.wiki_event_handler,
    PIPELINE: handlers.pipeline_handler,
}

class Context:
    """
    A class to pass all the parameters and shared values
    """
    def __init__(self, directory):
        self.directory = directory
        self.button_mode = MODE_NONE
        self.wait_for_verification = False
        self.config = None
        self.verified_chats = None
        self.table = None
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        file_handler = RotatingFileHandler('/var/log/gwt/gitlab-webhook-telegram.log', 'a', 1000000, 1)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_config(self):
        """
        Load the config file and transform it into a python usable var
        """
        try:
            with open(self.directory + 'config.json') as config_file:
                self.config = json.load(config_file)
        except Exception as e:
            self.logger.error("Impossible to read config.json file. Exception follows")
            self.logger.error(str(e))
            sys.exit()
        try:
            with open(self.directory + 'verified_chats.json') as verified_chats_file:
                self.verified_chats = json.load(verified_chats_file)
        except Exception as e:
            self.logger.error("Impossible to read verified_chats.json file. Exception follows")
            self.logger.error(str(e))
            sys.exit()
        try:
            with open(self.directory + 'chats_projects.json') as table_file:
                self.table = json.load(table_file)
        except Exception as e:
            self.logger.error("Impossible to read chats_projects.json file. Exception follows")
            self.logger.error(str(e))
            sys.exit()
        return self.config, self.verified_chats, self.table

    def write_verified_chats(self):
        """
        Save the verified chats file
        """
        with open(self.directory + 'verified_chats.json', 'w') as outfile:
            json.dump(self.verified_chats, outfile)

    def write_table(self):
        """
        Save the verified chats file
        """
        with open(self.directory + 'chats_projects.json', 'w') as outfile:
            json.dump(self.table, outfile)

    def is_authorized_project(self, token):
        """
        Test if the token is in the configuration
        """
        res = False
        for projet in self.config["gitlab-projects"]:
            if token == projet["token"]:
                res = True
        return res


class Bot:
    """
    A wrapper for the telegram bot
    """
    def __init__(self,token, context):
        self.token = token
        self.context = context
        self.updater = Updater(token=self.token)
        self.bot = self.updater.bot
        self.username = self.bot.username
        self.dispatcher = self.updater.dispatcher

        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        add_project_handler = CommandHandler('addProject', self.add_project)
        self.dispatcher.add_handler(add_project_handler)

        remove_project_handler = CommandHandler('removeProject', self.remove_project)
        self.dispatcher.add_handler(remove_project_handler)

        help_hanlder = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_hanlder)

        self.dispatcher.add_handler(CallbackQueryHandler(self.button))

        message_handler = MessageHandler(Filters.text, self.message)
        self.dispatcher.add_handler(message_handler)

        self.updater.start_polling()

    def send_message_to_list(self, list, message):
        """
        Send a message to all chat in list
        """
        for id in list:
            self.bot.send_message(id, message)

    def start(self, bot, update):
        """
        Defines the handler for /start command
        """
        chat_id = update.message.chat_id
        bot.send_message(chat_id=chat_id, text="Hi. I'm a simple bot triggered by GitLab webhooks.")
        if(self.context.config["configure-by-telegram"]):
            if chat_id in self.context.verified_chats:
                bot.send_message(chat_id=chat_id, text="Since your chat is verified, you can add project by typing /addProject")
            else:
                bot.send_message(chat_id=chat_id, text="First things first : you need to verify this chat. Just send the passphrase (if you don't want to, add the chat id : " + str(chat_id) + "  in the list of verified chats)")
                self.context.wait_for_verification = True
        else:
            bot.send_message(chat_id=chat_id, text="If you want to configure the bot with telegram, please set the 'configure-by-telegram' option to true in the settings.")


    def add_project(self,bot, update):
        """
        Defines the handler for /addProject command
        """
        chat_id = update.message.chat_id
        if(self.context.config["configure-by-telegram"]):
            if chat_id in self.context.verified_chats:
                self.context.button_mode = MODE_ADD_PROJECT
                inline_keyboard = []
                projects = [project for project in self.context.config["gitlab-projects"] if (project["token"] in self.context.table and chat_id not in self.context.table[project["token"]] or project["token"] not in self.context.table)]
                if len(projects) > 0:
                    for project in projects:
                        inline_keyboard.append([telegram.InlineKeyboardButton(text=project["name"], callback_data=project["token"])])
                    replyKeyboard = telegram.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
                    bot.send_message(chat_id=chat_id, reply_markup=replyKeyboard, text="Choose the project you want to add.")
                else:
                    bot.send_message(chat_id=chat_id, text="No project to add.")
            else:
                bot.send_message(chat_id=chat_id, text="This chat is no verified.")
        else:
            bot.send_message(chat_id=chat_id, text="If you want to configure the bot with telegram, please set the 'configure-by-telegram' option to true in the settings.")

    def remove_project(self, bot, update):
        """
        Defines the handler for /removeProject command
        """
        chat_id = update.message.chat_id
        if(self.context.config["configure-by-telegram"]):
            if chat_id in self.context.verified_chats:
                self.context.button_mode = MODE_REMOVE_PROJECT
                inline_keyboard = []
                projects = [project for project in self.context.config["gitlab-projects"] if (project["token"] in self.context.table and chat_id in self.context.table[project["token"]])]
                if len(projects) > 0:
                    for project in projects:
                        inline_keyboard.append([telegram.InlineKeyboardButton(text=project["name"], callback_data=project["token"])])
                    replyKeyboard = telegram.InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
                    bot.send_message(chat_id=chat_id, reply_markup=replyKeyboard, text="Choose the project you want to remove.")
                else:
                    bot.send_message(chat_id=chat_id, text="No project to remove.")
            else:
                bot.send_message(chat_id=chat_id)
        else:
            bot.send_message(chat_id=chat_id, text="If you want to configure the bot with telegram, please set the 'configure-by-telegram' option to true in the settings.")

    def button(self, bot, update):
        """
        Defines the handler for a click on button
        """
        query = update.callback_query
        if(self.context.button_mode == MODE_ADD_PROJECT):
            token = query.data
            chat_id = query.message.chat_id
            if token in self.context.table and chat_id in self.context.table[token]:
                bot.edit_message_text(text="Project was already there. Changing nothing.", chat_id=chat_id, message_id=query.message.message_id)
            else:
                if token not in self.context.table:
                    self.context.table[token] = []
                self.context.table[token].append(chat_id)
                self.context.write_table()
                bot.edit_message_text(text="The project was successfully added.", chat_id=chat_id, message_id=query.message.message_id)
            self.context.button_mode = MODE_NONE
        elif(self.context.button_mode == MODE_REMOVE_PROJECT):
            chat_id = query.message.chat_id
            token = query.data
            if token not in self.context.table or chat_id not in self.context.table[token]:
                bot.edit_message_text(text="Project was not there. Changing nothing.", chat_id=chat_id)
            else:
                self.context.table[token].remove(chat_id)
                self.context.write_table()
                bot.edit_message_text(text="The project was successfully removed.",chat_id=chat_id, message_id=query.message.message_id)
        else:
            pass

    def message(self, bot, update):
        """
        The handler in case a simple message is posted
        """
        if self.context.wait_for_verification:
            if update.message.text == self.context.config["passphrase"]:
                self.context.verified_chats.append(update.message.chat_id)
                self.context.write_verified_chats()
                bot.send_message(chat_id=update.message.chat_id, text="Ok. The chat is now verified")
                self.context.wait_for_verification = False
            else:
                bot.send_message(chat_id=update.message.chat_id, text="The passphrase is incorrect. Still waiting for verification")

    def help(self, bot, update):
        """
        Defines the handler for /help command
        """
        message = "Project gitlab-webhook-telegram v0.9\n"
        if(self.context.config["configure-by-telegram"]):
            message += "You have enabled configuration by telegram. You can use the following commands : \n\n/start : Use to verify the chat\n/addProject : add a project in this chat\n/removeProject : remove a project from this chat\n/help : Display this message\n\nIf you want to disable the configuration by telegram, you may change the setting configure-by-telegram to false."
        else:
            message += "You have disabled configuration by telegram. You can use the /help command to display this message. If you want to enable the configuration by telegram, you may change the setting configure-by-telegram to true."
        bot.send_message(chat_id=update.message.chat_id, text=message)


def get_RequestHandler(bot, context):
    """
    A wrapper for the RequestHandler class to pass parameters
    """
    class RequestHandler(BaseHTTPRequestHandler):
        """
        The server request handler
        """
        def __init__(self, *args, **kwargs):
            self.bot = bot
            self.context = context
            super(RequestHandler, self).__init__(*args, **kwargs)

        def _set_headers(self, code):
            """
            Send response with code and close headers
            """
            self.send_response(code)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_POST(self):
            """
            Handler for POST requests
            """
            token = self.headers['X-Gitlab-Token']
            if self.context.is_authorized_project(token):
                type = self.headers['X-Gitlab-Event']
                content_length = int(self.headers['Content-Length'])
                data = self.rfile.read(content_length)
                body = json.loads(data.decode('utf-8'))
                if type in HANDLERS:
                    if token in self.context.table and self.context.table[token]:
                        chats = [chat for chat in self.context.table[token] if chat in self.context.verified_chats]
                        HANDLERS[type](body, bot, chats)
                        self._set_headers(200)
                    else:
                        self.context.logger.info("No chats.")
                        self._set_headers(200)
                else:
                    self.context.logger.warn("No handler for the event " + type)
                    self._set_headers(404)
            else:
                self.context.logger.warn("Unauthorized project : token not in config.json")
                self._set_headers(403)
    return RequestHandler

class AppDaemon(Daemon):
    """
    A class to daemonize the app.
    Override init and run command
    """
    def __init__(self, pidfile, *args, **kwargs):
        self.directory = "/etc/gwt/"
        super(AppDaemon, self).__init__(pidfile, *args, **kwargs)

    def run(self):
        """
        run is called when the daemon starts or restarts
        """
        context = Context(self.directory)
        logger = context.logger
        logger.info("Starting gitlab-webhook-telegram app")
        logger.info("Getting configuration files")
        context.get_config()
        logger.info("config.json, chats_projects.json and verified_chats.json found. Using them for configuration.")
        logger.info("Getting bot with token " + context.config["telegram-token"])
        try:
            bot = Bot(context.config["telegram-token"], context)
            logger.info("Bot " + bot.username + " grabbed. Let's go.")
        except Exception as e:
            logger.error("Failed to grab bot. Stopping here the program.")
            logger.error("Exception : " + str(e))
            sys.exit()
        context.logger.info("Starting server on http://localhost:" + str(context.config["port"]))
        try:
            RequestHandler = get_RequestHandler(bot, context)
            httpd = socketserver.TCPServer(("", context.config["port"]), RequestHandler)
            httpd.serve_forever()
        except KeyboardInterrupt:
            logger.info("Keyboard interruption received. Shutting down the server")
        httpd.server_close()
        httpd.shutdown()
        logger.info("Server is down")
        os._exit(0)

def main():
    directory = os.path.dirname(os.path.realpath(__file__))+"/"
    daemon = AppDaemon('/tmp/gitlab-webhook-telegram.pid')
    arguments = docopt(__doc__, version="Gitlab-webhook-telegram 1.0")
    if arguments['start']:
        daemon.start()
    elif arguments['stop']:
        daemon.stop()
    elif arguments['restart']:
        daemon.restart()
    elif arguments['test']:
        daemon.run()

if __name__== "__main__":
    main()
