"""
This file defines all the handlers needed by the server
"""

V = 0
VV = 1
VVV = 2
VVVV = 3


def push_handler(data, bot, chats):
    """
    Defines the handler for a commit and push event
    """
    for chat in chats:
        verbosity = chat[1]
        for commit in data["commits"]:
            message = (
                "New commit on project "
                + data["project"]["name"]
                + "\nAuthor : "
                + commit["author"]["name"]
            )
            if verbosity != VVVV:
                message += "\nMessage: " + commit["message"].partition("\n")[0]
            else:
                message += "\nMessage: " + commit["message"]
            if verbosity >= VV:
                message += "\nUrl : " + commit["url"]

            bot.bot.send_message(chat_id=chat[0], text=message)


def tag_handler(data, bot, chats, verbosity):
    """
    Defines the handler for when tags ar pushed
    """
    for chat in chats:
        verbosity = chat[1]
        message = "New tag or tag removed on project " + data["project"]["name"]
        if verbosity >= VV:
            message += ". See " + data["project"]["web_url"] + "/tags for more information."
        bot.bot.send_message(chat_id=chat[0], text=message)


def issue_handler(data, bot, chats, verbosity):
    """
    Defines the handler for when a issue is created or changed
    """
    for chat in chats:
        verbosity = chat[1]
        oa = data["object_attributes"]
        message = ""
        if oa["confidential"]:
            message += "[confidential] "
        message += (
            "New issue or issue updated"
            + " on project "
            + data["project"]["name"]
            + "\nTitle : "
            + oa["title"]
        )
        if verbosity >= VVVV and oa["description"]:
            message += "\nDescription : " + oa["description"]
        message += "\nState : " + oa["state"] + "\nURL : " + oa["url"]
        if verbosity >= VVV:
            if "assignees" in data:
                assignees = ", ".join([x["name"] for x in data["assignees"]])
                message += "\nAssignee(s) : " + assignees
            labels = ", ".join([x["title"] for x in data["labels"]])
            if labels:
                message += "\nLabels : " + labels
            due_date = oa["due_date"]
            if due_date:
                message += "\nDue date : " + due_date
        bot.bot.send_message(chat_id=chat[0], text=message)


def note_handler(data, bot, chats, verbosity):
    """
    Defines the handler for a note (create or update) on commit, merge request, issue or snippet
    """
    for chat in chats:
        verbosity = chat[1]
        message = "New note on "
        if "commit" in data:
            message += "commit "
            info = "\nCommit : " + data["commit"]["url"]
        elif "merge_request" in data:
            message += "merge request "
            info = "\nMerge request : " + data["merge_request"]["title"]
        elif "issue" in data:
            message += "issue "
            info = "\nIssue : " + data["issue"]["title"]
        else:
            message += "snippet "
            info = "\nSnippet : " + data["snippet"]["title"]
        message += "on project " + data["project"]["name"]
        message += info
        message += "\nNote : " + data["object_attributes"]["note"]
        if verbosity >= VV:
            message += "\nURL : " + data["object_attributes"]["url"]
        bot.bot.send_message(chat_id=chat[0], text=message)


def merge_request_handler(data, bot, chats, verbosity):
    """
    Defines the handler for when a merge request is created or updated
    """
    for chat in chats:
        verbosity = chat[1]
        oa = data["object_attributes"]
        message = (
            "New merge request or merge request updated"
            + " on project "
            + data["project"]["name"]
            + "\nTitle : "
            + oa["title"]
            + "\nSource branch : "
            + oa["source_branch"]
            + "\nTarget branch : "
            + oa["target_branch"]
            + "\nMerge status : "
            + oa["merge_status"]
            + "\nState : "
            + oa["state"]
        )
        if verbosity >= VVV:
            labels = ", ".join([x["title"] for x in data["labels"]])
            if labels:
                message += "\nLabels : " + labels
            if "assignee" in data:
                message += "\nAssignee : " + data["assignee"]["username"]
        if verbosity >= VV:
            message += "\nURL : " + oa["url"]
        bot.bot.send_message(chat_id=chat[0], text=message)


def job_event_handler(data, bot, chats, verbosity):
    """
    Defines the handler for when a job begin or change
    """
    for chat in chats:
        verbosity = chat[1]
        message = (
            "New job or job updated on project "
            + data["repository"]["name"]
            + "\nbuild_status : "
            + data["build_status"]
            + "\nEnventual failure reason : "
            + data["build_failure_reason"]
        )
        if verbosity >= VV:
            message += "\nURL : " + data["repository"]["homepage"] + "/-/jobs"
        bot.bot.send_message(chat_id=chat[0], text=message)


def wiki_event_handler(data, bot, chats, verbosity):
    """
    Defines the handler for when a wiki page is created or changed
    """
    for chat in chats:
        verbosity = chat[1]
        message = "New wiki page or wiki page updated on project " + data["project"]["name"]
        if verbosity >= VV:
            message += "\nURL : " + data["wiki"]["web_url"]
        bot.bot.send_message(chat_id=chat[0], text=message)


def pipeline_handler(data, bot, chats, verbosity):
    """
    Defines the hander for when a pipelin begin or change
    """
    for chat in chats:
        verbosity = chat[1]
        message = (
            "New pipeline or pipeline updated on project "
            + data["project"]["name"]
            + "\nStatus : "
            + data["object_attributes"]["status"]
        )
        if verbosity >= VV:
            message += "\nURL : " + data["project"]["web_url"] + "/pipelines"
        bot.bot.send_message(chat_id=chat[0], text=message)
