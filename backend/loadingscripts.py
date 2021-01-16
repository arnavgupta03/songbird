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
        if "https://t.co" in tweet:
            tweets[i] = tweet.replace(tweet[tweet.index("https://t.co"):], '')
    return tweets

def listToString(tweets):
    sTweets = ""
    for tweet in tweets:
        sTweets += tweet
    return sTweets

def onlyAlphabet(sTweets):
    toRemove = []

    for i in range(len(sTweets)):
        if sTweets[i].isdigit() or sTweets[i].isalpha():
            toRemove.append(i)

    for i in toRemove:
        sTweets = sTweets[:i] + sTweets[(i + 1):]
    return sTweets