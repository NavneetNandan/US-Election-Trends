from flask import Flask, render_template
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)
app.debug = True


@app.route('/')
def hello_world():
    DATABASE_NAME = 'uselectiontrends'
    client = MongoClient()
    db = client[DATABASE_NAME]
    tweets = db['tweets'].find()
    counted_retweeted = 0
    counted_original = 0
    counted_text_only = 0
    counted_image_only = 0
    counted_text_image_both = 0
    favourite_counts = []
    places_of_tweets = {}
    for tweet in tweets:
        favourite_counts.append(tweet.get("favorite_count"))
        if tweet.__contains__("retweeted_status"):
            counted_retweeted = counted_retweeted + 1
        else:
            counted_original += 1
        if tweet['place'] != None:
            tweet_place_full_name = tweet['place']['full_name']
            if places_of_tweets.__contains__(tweet_place_full_name):
                places_of_tweets[tweet_place_full_name] += 1
            else:
                places_of_tweets[tweet_place_full_name] = 1
        if (tweet.__contains__("text")):
            if (len(tweet['text']) != 0):
                if (tweet['entities'].__contains__('media')):
                    counted_text_image_both += 1
                else:
                    counted_text_only += 1
            else:
                counted_image_only += 1
        else:
            if (tweet['entities'].__contains__('media')):
                counted_image_only += 1
    print(counted_image_only)
    print(counted_text_only)
    print(counted_text_image_both)
    text_only_percent = ((counted_text_only) /( counted_text_image_both + counted_text_only + counted_image_only) )* 100
    image_only_percent = ((counted_image_only) / (counted_text_image_both + counted_text_only + counted_image_only) )* 100
    text_image_both_percent = ((
                               counted_text_image_both) / (counted_text_image_both + counted_text_only + counted_image_only)) * 100
    original_tweet_percent = (counted_original / (counted_original + counted_retweeted)) * 100
    retweeted_tweet_percent = (counted_retweeted / (counted_original + counted_retweeted)) * 100
    # print(favourite_counts)
    # plt.hist(favourite_counts)
    # plt.show()
    return render_template("USelections.html", hashtags=top10_hashtags_in_election(),
                           original_tweet_percent=original_tweet_percent,
                           retweeted_tweet_percent=retweeted_tweet_percent, places_of_tweets=places_of_tweets,
                           text_only_percent=text_only_percent, text_image_both_percent=text_image_both_percent,
                           image_only_percent=image_only_percent,counted_image_only=counted_image_only,counted_text_image_both=counted_text_image_both,counted_text_only=counted_text_only,counted_original=counted_original,counted_retweeted=counted_retweeted)


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
    all_hashtags_pandas_series.sort_values(inplace=True, ascending=False)
    top10_hashtags = all_hashtags_pandas_series[0:10].keys()
    return top10_hashtags


if __name__ == '__main__':
    app.run()
