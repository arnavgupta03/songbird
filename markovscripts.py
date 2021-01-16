import markovify

def chain(tweets):
    text_model = markovify.Text(tweets)

    strings = ""
    
    strings += str(text_model.make_short_sentence(200))

    return strings