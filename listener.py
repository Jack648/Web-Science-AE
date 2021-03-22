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
fear = ['#fear', '#disgust', '#fears', '#anxiety', '😨', '#scared', '#anxious']
angry = ['#anger', '#angry', '#angers', '#angerissues', '#angerfist', '😡', '🤬', '😠']

currentWords = angry  ##input the categoty you want to search
otherWords = Excitement + Happy + Pleasant + badSurprise + fear + angry
print(otherWords)
for word in currentWords:  # removes words that are being searched for from validation
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
emotionDatabase = db.newangrytweets  ##name the database what you want


class myStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:  ##if there is a extended tweet
            checker = 1
            fulltext = str(status.extended_tweet["full_text"])
            fulltext = fulltext.replace('\n', ' ').replace('\r', '')
            fulltext = contractions.fix(fulltext)  ##removes contractions from the text
            fulltext = cleaner(fulltext)
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
        except AttributeError:  ##if there is no extended tweet
            checker = 1
            fulltext = str(status.text)
            fulltext = fulltext.replace('\n', ' ').replace('\r', '')
            fulltext = contractions.fix(fulltext)
            fulltext = cleaner(fulltext)
            status._json["clean"] = fulltext
            for word in otherWords:
                if word in status._json["clean"]:
                    print("overlap")
                    checker = 0  ##if overlap found
                    pass
            if checker == 1:  ##if no overlap found
                if emotionDatabase.count_documents({'clean': status._json["clean"]}) < 1:
                    print(status._json["clean"])
                    emotionDatabase.insert_one(status._json)

        if emotionDatabase.estimated_document_count() > 299:  ##if the database has more then 299 tweets then stop
            myStream.disconnect()
            print("disconected")

    def on_error(self, status_code):
        print(status_code)  # 420 means to many


myStreamListener = myStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(track=currentWords, languages=['en'])
