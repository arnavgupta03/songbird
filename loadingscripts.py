import re
import emoji

def onlyText(tweets):
    for i, tweet in enumerate(tweets):
        tweets[i] = tweet['text']
    return tweets

def cleanRT(tweets):
    for i, tweet in enumerate(tweets):
        if (tweet[0] == "R" and tweet[1] == "T" and tweet[3] == "@"):
            tweets[i] = tweet[(tweet.index(":") + 2):]
    return tweets

def cleanEnd(tweets):
    for i, tweet in enumerate(tweets):
        if "https://t." in tweet:
            tweets[i] = tweet.replace(tweet[tweet.index("https://t."):], '')
    return tweets

def listToString(tweets):
    sTweets = ""
    for tweet in tweets:
        sTweets += tweet
    return sTweets

def onlyAlphabet(sTweets):
    sTweets = sTweets.replace('…', '')
    sTweets = sTweets.replace('#', '')
    sTweets = sTweets.replace('@', '')
    return sTweets

def deEmojify(text):
    return re.sub(emoji.get_emoji_regexp(), r"", text)

def getAllGenres(genres):
    sGenre = ""

    for genrelist in genres:
        for genre in genrelist:
            sGenre += genre
            sGenre += " "