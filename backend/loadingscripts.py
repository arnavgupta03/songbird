def onlyText(tweets):
    for i, tweet in enumerate(tweets):
        tweets[i] = tweet['text']
    return tweets

def cleanRT(tweets):
    for i, tweet in enumerate(tweets):
        if (tweet[0] == "R" and tweet[1] == "T" and tweet[3] == "@"):
            tweets[i] = tweet[(tweet.index(":") + 2):]
    return tweets