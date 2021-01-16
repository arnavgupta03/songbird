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