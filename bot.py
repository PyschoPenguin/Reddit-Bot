import praw
import datetime
import time
import os

swear_words = ["fuck", "shit", "cunt", "ass", "asshole", "twat", "cock"]

blacklisted_subreddit_filename = "C:\\Users\\Gutman\\Desktop\\Reddit_Bot\\blacklisted_subreddits.txt"
blacklisted_users_filename = "C:\\Users\\Gutman\\Desktop\\Reddit_Bot\\blacklisted_users.txt"
posts_replied_filename = "C:\\Users\\Gutman\\Desktop\\Reddit_Bot\\posts_replied.txt"
comments_replied_filename = "C:\\Users\\Gutman\\Desktop\\Reddit_Bot\\comment_replied.txt"

exclude_nsfw_string = "-nsfw"

bot_name = "UserInfo_Bot"
test_subreddit = "PythonInfoBotTest"
call_word = "call userinfo_bot" 

reddit = praw.Reddit("bot1")
bot_profile = reddit.redditor(bot_name)

#var = reddit.redditor(reddit.user.karma) - karma
#var = reddit.redditor(reddit.user.subreddits) - subbed subreddits
#var = reddit.inbox.messages(limit=None)


#TODO - Create a log file?
#TODO - Check if subreddit is banned, if so, don't reply.

# # # # # # # # # # # # # # # # # # #

def UserPostKarma(reddit, username):
    return reddit.redditor(username).link_karma

# # # # #

def GetHotScore(reddit, username, isPost):
    if isPost:
        for post in reddit.redditor(username).submissions.top("all"):
            return post.score
    elif not isPost:
        for comment in reddit.redditor(username).comments.top("all"):
            return comment.score

def GetHotSubmissionLink(reddit, username):
    for post in reddit.redditor(username).submissions.top("all"):
        return post.url

# # # # #

def GetRecent(reddit, username, isPost):
    if isPost:
        for recentPost in reddit.redditor(username).submissions.new(limit=1):
            return datetime.datetime.fromtimestamp(recentPost.created)
    elif not isPost:
        for recentComment in reddit.redditor(username).submissions.new(limit=1):
            return datetime.datetime.fromtimestamp(recentComment.created)

# # # # #

# TODO - Refactor swear retrival.
# TODO - GET TO WORK!!!

def GetSwearWords(reddit, username, isPost):
    count = 0
    if isPost:
        for post in reddit.redditor(username).submissions.hot(limit=10):
            for i in range(len(swear_words)):
                if "fuck" in post.selftext:
                    count += 1
    elif not isPost:
        for comment in reddit.redditor(username).comments.new(limit=10):
            for i in range(len(swear_words)):
                if "fuck" in comment.body:
                    count += 1
    return count
            
# # # # # # # # # # # # # # # # # # #

def TextToList(filepath):
    return_list = []
    if os.path.isfile(filepath):
        with open(filepath, "r") as f:
            return_list = f.read()
            return_list = return_list.split("\n")
            return_list = list(filter(None, return_list))
    return return_list


# # # # # # # # # # # # # # # # # # #

def CheckCommentScore():
    limit = 500
    removeThreshold = 0

    for botComment in bot_profile.comments.new(limit=limit):
        if botComment.score < removeThreshold:
            botComment.delete()


# Blacklist Functions #

def BlacklistUser(reddit):
    filepath = blacklisted_users_filename
    id = "6k79wh"
    blacklistSubmission = reddit.submission(id).comments
    for comments in blacklistSubmission:
        if comments.body[:3] == "/u/":
            blacklisted_users.append(comments.body)
            with open(filepath, "w") as f:
                f.write(comments.body + "\n")
    print("Done")
    
def BlacklistSubreddit(reddit):
    filepath = blacklisted_subreddit_filename
    id = "6k79wh"
    blacklistSubmission = reddit.submission(id).comments
    for comments in blacklistSubmission:
        if comments.body[:3] == "/r/":
            blacklisted_subs.append(comments.body)
            with open(filepath, "w") as f:
                f.write(comments.body)
    print("Done")    

# Id Functions

def ClearIDs(filepath):
    f = open(filepath, "w").truncate()

def FileContainsID(filepath, id):
    if id in open(filepath).read():
        return True
    return False


# Useful Functions

def MessageUser(reddit, username, subject, body):
    print("Messaging {name}")
    redditor = reddit.redditor(username).message(subject, body)
    time.sleep(5)

def ReplyToComments(reddit, subreddit, amount):
    if amount > 1:
        print("Recieving {amount} comments.".format(amount=amount))
    else:
        print("Receiving {amount} comment.".format(amount=amount))
    
    for i in range(len(blacklisted_subs)):
        if subreddit in blacklisted_subs[i][3:]:
            return

    for comment in reddit.subreddit(subreddit).comments(limit=amount):
        if call_word in comment.body and comment.author != reddit.user.me:
            for i in range(len(blacklisted_users)):
                if comment.author.name in blacklisted_users[i][3:]: 
                    return
            if not FileContainsID(comments_replied_filename, comment.id):
                if comment.score > 0:
                    exclude_nsfw = exclude_nsfw_string not in comment.body[-5:]

                    reply = CommentReply(comment, exclude_nsfw)
                    print("Replying to comment...")
                    print(comment.body)
                    comment.reply(reply)

                    #with open(comments_replied_filename, "a") as f:
                     #   f.write(comment.id + "\n")

# TODO - Find a way to clean this up.

def CommentReply(comment, nsfw):
    user_post_karma = UserPostKarma(reddit, comment.author.name)
    user_hot_comment = GetHotScore(reddit, comment.author.name, False)
    user_hot_post = GetHotScore(reddit, comment.author.name, True)

    user_recent_post = GetRecent(reddit, comment.author.name, True)
    user_recent_comment = GetRecent(reddit, comment.author.name, False)

    if nsfw:
        comment_reply = "UserInfoBot: *{caller}* [NSFW Version]".format(caller=comment.author.name)
        comment_reply += "\n\n"
        comment_reply += "User Post Karma: {karma}".format(karma=user_post_karma)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Most Recent Post: {recent}".format(caller=comment.author.name, recent=user_recent_post)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Most Recent Comment: {recent}".format(caller=comment.author.name, recent=user_recent_comment)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Hot Comment: {hot} upvotes".format(caller=comment.author.name, hot=user_hot_comment)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Hot Post: {hot} upvotes @ {link}".format(caller=comment.author.name, hot=user_hot_post, link=GetHotSubmissionLink(reddit, comment.author.name))
        comment_reply += "\n\n"
        comment_reply += "Swear Words for {caller} in Last 10 Comments: {swearComments}".format(caller=comment.author.name, swearComments=GetSwearWords(reddit, comment.author.name, False))
        comment_reply += "\n\n"
        comment_reply += "Swear Words for {caller} in Last 10 Posts: {swearPosts}".format(caller=comment.author.name, swearPosts=GetSwearWords(reddit, comment.author.name, True))
        comment_reply += "\n\n" + "***" + "\n\n"
        comment_reply += "^I'm ^a ^bot. ^| ^Creator: ^/u/PyschoPenguin ^| ^[Blacklist](https://www.reddit.com/r/PythonInfoBotTest/comments/6k79wh/blacklist/)"
    elif not nsfw:
        comment_reply = "UserInfoBot: *{caller}*".format(caller=comment.author.name)
        comment_reply += "\n\n"
        comment_reply += "User Post Karma: {karma}".format(karma=user_post_karma)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Most Recent Post: {recent}".format(caller=comment.author.name, recent=user_recent_post)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Most Recent Comment: {recent}".format(caller=comment.author.name, recent=user_recent_comment)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Hot Comment: {hot} upvotes".format(caller=comment.author.name, hot=user_hot_comment)
        comment_reply += "\n\n"
        comment_reply += "{caller}'s Hot Post: {hot} upvotes @ {link}".format(caller=comment.author.name, hot=user_hot_post, link=GetHotSubmissionLink(reddit, comment.author.name))
        comment_reply += "\n\n" + "***" + "\n\n"
        comment_reply += "^I'm ^a ^bot. ^| ^Creator: ^/u/PyschoPenguin ^| ^[Blacklist](https://www.reddit.com/r/PythonInfoBotTest/comments/6k79wh/blacklist/)"
    return comment_reply

blacklisted_subs = TextToList(blacklisted_subreddit_filename)
blacklisted_users = TextToList(blacklisted_users_filename)
posted_comments_id = TextToList(comments_replied_filename)

ReplyToComments(reddit, test_subreddit, 5)
