import praw
import pandas as pd
import json

reddit_read_only = praw.Reddit(client_id='sO_jaNad60v0cSTEIFebYg', client_secret='Imsd0n3zHijSElD4Sa4L7lv1lV0b2w', user_agent='Crawler')

subreddit = reddit_read_only.subreddit("movies")
comments = {}
#master_data = {}

# # Display the name of the Subreddit
print("Display Name:", subreddit.display_name)

# # Display the title of the Subreddit
print("Title:", subreddit.title)

# # Display the description of the Subreddit
print("Description:", subreddit.description)

'''
# controversial, gilded, hot, new, rising, top
# https://praw.readthedocs.io/en/latest/getting_started/quick_start.html#submission-iteration

# for each function add parameter "time_filter" = "all", "day", "hour", "month", "week", or "year"
# https://praw.readthedocs.io/en/stable/code_overview/models/subreddit.html
'''

# TOP -----------------------------------------------------------------------------------------
posts = subreddit.top(time_filter="all")
# Scraping the top posts of the current month

posts_dict = {"Title": [], "Post Text": [],
              "ID": [], "Score": [],
              "Total Comments": [], "Post URL": []
              }

for post in posts:
    # Title of each post
    posts_dict["Title"].append(post.title)

    # Text inside a post
    posts_dict["Post Text"].append(post.selftext)

    # Unique ID of each post
    posts_dict["ID"].append(post.id)

    # The score of a post
    posts_dict["Score"].append(post.score)

    # Total number of comments inside the post
    posts_dict["Total Comments"].append(post.num_comments)

    # URL of each post
    posts_dict["Post URL"].append(post.url)

# Saving the data in a pandas dataframe
top_posts = pd.DataFrame(posts_dict)

top_posts.to_csv("top_posts.csv", index=True)

with open('top_comments.json', 'a') as f:
    f.write('[')

for id in top_posts['ID']:
    print(id)
    submission = reddit_read_only.submission(str(id))
    submission.comments.replace_more(limit=None)
    for count, comment in enumerate(submission.comments.list()):
        comments['comment'+str(count)] = comment.body.encode('ascii','ignore').decode("utf-8")
    with open('top_comments.json', 'a') as f:
        json.dump(comments, f)
        f.write(',\n')

with open('top_comments.json', 'a') as f:
    f.write(']')