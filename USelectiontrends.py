from flask import Flask, render_template
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)
app.debug = True
DATABASE_NAME = 'uselectiontrends'


uri="mongodb://navneet8:cricket00@ds019470.mlab.com:19470/uselectiontrends"

@app.route('/')
def create_page():
    client = MongoClient()
    # client = MongoClient()
    db = client[DATABASE_NAME]
    tweets = db['tweets'].find()  # getting all tweets from mongoDB database
    counted_retweeted = 0
    counted_original = 0
    counted_text_only = 0
    counted_image_only = 0
    counted_text_image_both = 0
    favourite_counts = []
    places_of_tweets = {}
    all_hashtags_map = {}
    trump_score=0
    clinton_score=0
    total_tweet = db.tweets.count()
    for tweet in tweets:
        favourite_counts.append(tweet.get("favorite_count"))
        # finding hashtags associated with each tweet
        hashtags_of_tweet = tweet.get("entities").get("hashtags")
        # storing each hashtag of twitter in dictionary as key and value as number of apperaings in any tweet
        for hashtag in hashtags_of_tweet:
            hashtag_text = hashtag.get("text")
            if(hashtag_text.lower()=='trump' or hashtag_text.lower()=='donaldtrump'):
                trump_score+=2
            elif(hashtag_text.lower()=='clinton' or hashtag_text.lower()=='hillary' or hashtag_text.lower()=='hillaryclinton'):
                clinton_score+=2
            if all_hashtags_map.__contains__(
                    hashtag_text):  # if hashtag already exists in dictionary then increase the count
                all_hashtags_map[hashtag_text] = int(all_hashtags_map[hashtag_text]) + 1
            else:  # else create key and initialize count with 1
                all_hashtags_map[hashtag_text] = 1
        usermentions_of_tweet = tweet.get("entities").get("user_mentions")
        for user in usermentions_of_tweet:
            if(user.get('id')==25073877):
                trump_score+=4
            elif(user.get('id')==1339835893):
                clinton_score+=4
        # finding count of retweeted tweets and original tweets
        if tweet.__contains__("retweeted_status"):
            userid_of_author_of_original_tweet=tweet.get("retweeted_status").get("user").get("id")
            if(userid_of_author_of_original_tweet==25073877):
                trump_score+=10
            elif(userid_of_author_of_original_tweet==1339835893):
                clinton_score+=10
            counted_retweeted += 1
        else:
            counted_original += 1
        if tweet['place'] is not None:
            # finding location (City name) of each tweet if it has related information attached
            tweet_place_full_name = tweet['place']['full_name']
            # store location in a python dictionary as key with value as number of tweets from same location
            if places_of_tweets.__contains__(tweet_place_full_name):
                places_of_tweets[tweet_place_full_name] += 1
            else:
                places_of_tweets[tweet_place_full_name] = 1
        # finding type of tweet
        if tweet.__contains__("text"):
            if len(tweet['text']) != 0:  # if text is not empty
                if tweet['entities'].__contains__('media'):  # if there is any image in tweet with text
                    counted_text_image_both += 1
                else:  # no image and there is text in tweet
                    counted_text_only += 1
            else:  # no text
                counted_image_only += 1
        else:
            if tweet['entities'].__contains__('media'):
                counted_image_only += 1

    all_hashtags_pandas_series = pd.Series(
        all_hashtags_map)  # storing all hashtag dictionary in pandas series for optimised analysis
    all_hashtags_pandas_series.sort_values(inplace=True, ascending=False)  # sorting series descending order
    top10_hashtags = all_hashtags_pandas_series[0:10].keys()  # getting top 10 hashtag
    print("cln")
    print(clinton_score)
    print("trm")
    print(trump_score)
    return render_template("USelections.html",
                           hashtags=top10_hashtags,
                           places_of_tweets=places_of_tweets,
                           counted_image_only=counted_image_only,
                           counted_text_image_both=counted_text_image_both,
                           counted_text_only=counted_text_only,
                           counted_original=counted_original,
                           counted_retweeted=counted_retweeted,
                           total_tweets=total_tweet,
                           clinton_score=(clinton_score/(trump_score+clinton_score))*10,
                           trump_score=(trump_score/(trump_score+clinton_score))*10)


if __name__ == '__main__':
    app.run()
