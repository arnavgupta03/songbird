import markovify

def chain(tweets):
    text_model = markovify.Text(tweets, state_size = 2)

    strings = ""
    
    strings = str(text_model.make_sentence(tries = 1000))

    if strings == "None":
        return tweets[:100]
    else:
        return strings

#print(chain("The yogi of India swear by its restorative powers and at 99, IT CLEARLY WORKS! Happy birthday BettyMWhite! why is janurary giving me wednesday energyall me and ariel do is stay up til 4:30am validating each other’s thoughts and dreams &amp; be gayLiterally nothing I have done as a front end web dev has been as important as anyone who has ever cooked a single m A king was born today. Happy birthday, Song Kang-ho! 생일 축하합니다 송강호 Ik he's kind of a meme coz of Reddit but like, Danny DeVito is an actual all things considereddang guess my gender is your dad"))