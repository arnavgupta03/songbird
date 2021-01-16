from flask import Flask, render_template, redirect, request, url_for, session
from decouple import config
from authlib.integrations.flask_client import OAuth, OAuthError
from loadingscripts import cleanRT, onlyText, cleanEnd, listToString, onlyAlphabet
from markovscripts import chain

app = Flask(__name__)
app.secret_key = config('ACCESS_SECRET')
app.config.from_object('config')

oauth = OAuth(app)
oauth.register(
    name='twitter',
    api_base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    fetch_token=lambda: session.get('token'),
)

"""@app.errorhandler(OAuthError)
def handle_error(error):
    return render_template('error.html', error=error)"""

@app.route('/')
def homepage():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.twitter.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.twitter.authorize_access_token()
    url = 'account/verify_credentials.json'
    resp = oauth.twitter.get(url)
    profile = resp.json()
    session['token'] = token
    session['user'] = profile
    return redirect('/tweets')

@app.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('user', None)
    return redirect('/')

@app.route('/tweets')
def tweets():
    url = 'statuses/home_timeline.json'
    params = {'count': 200, 'trim_user': True, 'exclude_replies': True, 'include_entities': False}
    prev_id = request.args.get('prev')
    if prev_id:
        params['max_id'] = prev_id

    resp = oauth.twitter.get(url, params = params)
    tweets = resp.json()
    tweets = onlyText(tweets)
    tweets = cleanRT(tweets)
    tweets = cleanEnd(tweets)
    sTweets = listToString(tweets)
    #sTweets = onlyAlphabet(sTweets)
    return render_template('tweets.html', tweets = tweets, sTweets = sTweets)

if __name__ == '__main__':
    app.run(debug=True)