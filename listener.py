import pymongo
from pymongo import MongoClient
import json
import tweepy
import twitter
from pprint import pprint
import configparser
import pandas as pd
import tweepy
import csv
import json
import re
import pandas as pd
import numpy as np
import sys
import contractions


def cleaner(text):
    text = re.sub(r'@[A-Za-z0-9:_]+', '', text)  # removed @mentions
    # text = re.sub(r'#', '', text)  # Removing the # symbol
    text = re.sub(r'RT[\s]+', '', text)  # remove retweets
    text = re.sub(r'https?://\S+', '', text)  # remove hyerlink
    text = re.sub(r"^\s+", "", text)  # removes starting spaces
    text = re.sub(r'([A-Za-z])\1{3,}', r'\1', text)  # remove paaaaarty and replaces with party
    return text


Excitement = ['#excitement', '#excited', '#exciting', '#soexcited', '🤗', '#enthusiasm', '#excitementawaits',
              '#excitements']
Happy = ['#happy', '#happytoday', '#behappy', '#happyme', '😀', '☺']
Pleasant = ['#pleasant', '#pleasantsurprise', '#pleasantweather', '#pleasantlysuprised', '😌']
badSurprise = ['#disappointment ', '#disappointed', '#takenaback', '😞']
fear = ['#fear', '#disgust', '#fears', '#anxiety', '😨', '#scared','#anxious']
angry = ['#anger', '#angry', '#angers', '#angerissues', '#angerfist', '😡', '🤬', '😠']

currentWords = angry
otherWords = Excitement + Happy + Pleasant + badSurprise + fear + angry
print(otherWords)
for word in currentWords:
    otherWords.remove(word)

consumer_key = "0PH6TtHoBum8pZ0P8oOpoQix8"
consumer_secret = "rjJCo3LYegxBHHQ2gYXrxe0V7yi2979LykWZSDhSZeK1wCaJLf"
access_token = "1356562505091416064-56CxdPqnLGKLFrjHvagAbxM1BiTUHW"
access_token_secret = "32ocB4DjzsZkU82zAb7rMRnWaeFp2aRN1Gmu4j1OIalTQ"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

client = pymongo.MongoClient()
db = client.emotions
emotionDatabase = db.angrytweets


class myStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            checker = 1
            fulltext = str(status.extended_tweet["full_text"])
            fulltext = fulltext.replace('\n', ' ').replace('\r', '')
            #  print(fulltext)
            fulltext = contractions.fix(fulltext)
            #  print(fulltext)
            fulltext = cleaner(fulltext)
            #    print(fulltext)
            status._json["clean"] = fulltext
            for word in otherWords:

                if word in status._json["clean"]:
                    print("overlap")
                    checker = 0
                    pass
            # print(fulltext)
            if checker == 1:
                if emotionDatabase.count_documents({'clean': status._json["clean"]}) < 1:
                    print(status._json["clean"])
                    emotionDatabase.insert_one(status._json)
        except AttributeError:
            checker = 1
            fulltext = str(status.text)
            fulltext = fulltext.replace('\n', ' ').replace('\r', '')
            # print(fulltext)
            fulltext = contractions.fix(fulltext)
            # print(fulltext)
            fulltext = cleaner(fulltext)
            # print(fulltext)
            status._json["clean"] = fulltext
            for word in otherWords:
                if word in status._json["clean"]:
                    print("overlap")
                    checker = 0
                    pass
            if checker == 1:
                if emotionDatabase.count_documents({'clean': status._json["clean"]}) < 1:
                    print(status._json["clean"])
                    emotionDatabase.insert_one(status._json)

        if emotionDatabase.estimated_document_count() > 299:
            myStream.disconnect()
            print("disconected")

    def on_error(self, status_code):
        print(status_code)  # 420 means to many


# print(happytweets.estimated_document_count())
# user_cursor = happytweets.distinct("text")
# print(user_cursor)
# print(len(user_cursor))

# for words in otherWords:
#    if words in user_cursor.text:


myStreamListener = myStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(track=currentWords, languages=['en'])
# myStream.disconect()
# (happytweets.estimated_document_count())
