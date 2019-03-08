"""
This file defines all the handlers needed by the server
"""

def push_handler(data, bot, chats):
    """
    Defines the handler for a commit and push event
    """
    for commit in data["commits"]:
        message = "New commit on project " + data["project"]["name"] + "\nAuthor : " + commit["author"]["name"] + "\nMessage : " + commit["message"] + "\nUrl : " + commit["url"]
        bot.send_message_to_list(chats, message)

def tag_handler(data, bot, chats):
    """
    Defines the handler for when tags ar pushed
    """
    message = "New tag or tag removed on project " + data["project"]["name"] + ". See " + data["project"]["web_url"] + "/tags for more information."
    bot.send_message_to_list(chats, message)

def issue_handler(data, bot, chats):
    """
    Defines the handler for when a issue is created or changed
    """
    oa = data["object_attributes"]
    message = ""
    if oa["confidential"]:
        message += "[confidential] "
    message += "New issue or issue updated" + " on project " + data["project"]["name"] + "\nTitle : " + oa["title"]
    if oa["description"]:
        message += "\nDescription : " + oa["description"]
    message += "\nState : " + oa["state"] + "\nURL : " + oa["url"]
    if "assignees" in data:
        assignees = ", ".join([x["name"] for x in data["assignees"]])
        message += "\nAssignee(s) : " + assignees
    labels = ", ".join([x["title"] for x in data["labels"]])
    if labels:
        message += "\nLabels : " + labels
    due_date = oa["due_date"]
    if due_date:
        message += "\nDue date : " + due_date
    bot.send_message_to_list(chats, message)

def note_handler(data, bot, chats):
    """
    Defines the handler for a note (create or update) on commit, merge request, issue or snippet
    """
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
        ifno = "\nSnippet : " + data["snippet"]["title"]
    message += "on project " + data["project"]["name"]
    message += info
    message += "\nNote : " + data["object_attributes"]["note"]
    message += "\nURL : " + data["object_attributes"]["url"]
    bot.send_message_to_list(chats, message)

def merge_request_handler(data, bot, chats):
    """
    Defines the handler for when a merge request is created or updated
    """
    oa = data["object_attributes"]
    message = "New merge request or merge request updated" + " on project " + data["project"]["name"] + "\nTitle : " + oa["title"] + "\nSource branch : " + oa["source_branch"] + "\nTarget branch : " + oa["target_branch"] + "\nMerge status : " + oa["merge_status"] + "\nState : " + oa["state"]
    labels = ", ".join([x["title"] for x in data["labels"]])
    if labels:
        message += "\nLabels : " + labels
    if "assignee" in data:
        message += "\nAssignee : " + data["assignee"]["username"]
    message += "\nURL : " + oa["url"]
    bot.send_message_to_list(chats, message)

def job_event_handler(data, bot, chats):
    """
    Defines the handler for when a job begin or change
    """
    message = "New job or job updated on project " + data["repository"]["name"] + "\nbuild_status : " + data["build_status"] + "\nEnventual failure reason : " + data["build_failure_reason"] + "\nURL : " + data["repository"]["homepage"] +"/-/jobs"
    bot.send_message_to_list(chats, message)

def wiki_event_handler(data, bot, chats):
    """
    Defines the handler for when a wiki page is created or changed
    """
    message = "New wiki page or wiki page updated on project " + data["project"]["name"] + "\nURL : " + data["wiki"]["web_url"]
    bot.send_message_to_list(chats, message)

def pipeline_handler(data, bot, chats):
    """
    Defines the hander for when a pipelin begin or change
    """
    message = "New pipeline or pipeline updated on project " + data["project"]["name"] + "\nStatus : " + data["object_attributes"]["status"] + "\nURL : " + data["project"]["web_url"] + "/pipelines"
    bot.send_message_to_list(chats, message)