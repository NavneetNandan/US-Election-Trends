from flask import Flask, render_template
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)


@app.route('/')
def hello_world():
    DATABASE_NAME = 'uselectiontrends'
    client = MongoClient()
    db = client[DATABASE_NAME]
    tweets = db['tweets'].find()
    counted_retweeted = 0
    counted_original=0
    for tweet in tweets:
        if (tweet.__contains__("retweeted_status")):
            # print("retweeted")
            counted_retweeted = counted_retweeted + 1
        else:
            # print("original")
            counted_original += 1
    print(counted_retweeted)
    print(counted_original)
    original_tweet_percent=(counted_original/(counted_original+counted_retweeted))*100
    retweeted_tweet_percent=(counted_retweeted/(counted_original+counted_retweeted))*100
    return render_template("USelections.html", hashtags=top10_hashtags_in_election(),
                           original_tweet_percent=original_tweet_percent,
                           retweeted_tweet_percent=retweeted_tweet_percent)


def top10_hashtags_in_election():
    """

    :rtype: list
    """
    DATABASE_NAME = 'uselectiontrends'
    client = MongoClient()
    db = client[DATABASE_NAME]
    tweets = db['tweets'].find()
    all_hashtags_map = {}
    for tweet in tweets:
        hashtags_of_tweet = tweet.get("entities").get("hashtags")
        for hashtag in hashtags_of_tweet:
            hashtag_text = hashtag.get("text")
            if all_hashtags_map.__contains__(hashtag_text):
                all_hashtags_map[hashtag_text] = int(all_hashtags_map[hashtag_text]) + 1
            else:
                all_hashtags_map[hashtag_text] = 1
    all_hashtags_pandas_series = pd.Series(all_hashtags_map)
    all_hashtags_pandas_series.sort_values(inplace=True,ascending=False)
    top10_hashtags = all_hashtags_pandas_series[0:10].keys()
    return top10_hashtags


if __name__ == '__main__':
    app.run()
