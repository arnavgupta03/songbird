from flask import Flask, render_template, redirect, request, url_for, session
from decouple import config
from authlib.integrations.flask_client import OAuth, OAuthError
from loadingscripts import cleanRT, onlyText, cleanEnd, listToString, onlyAlphabet, deEmojify
from markovscripts import chain
import base64, json, requests
from urllib.parse import quote

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

markovified = ""

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
    sTweets = onlyAlphabet(sTweets)
    sTweets = deEmojify(sTweets)
    markovified = chain(sTweets)
    session['markovified'] = markovified
    #return render_template('tweets.html', tweets = tweets, sTweets = sTweets, markovified = markovified)
    return redirect('/login-spotify')

SPOTIFY_CLIENT_ID = config("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = config("SPOTIFY_CLIENT_SECRET")
SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'

SPOTIFY_REDIRECT_URI = 'http://localhost:5000/authorize_spotify'
SPOTIFY_SCOPES = 'user-top-read playlist-modify-private'
SPOTIFY_STATE = ""
SPOTIFY_SHOW_DIALOG = 'true'

spotify_auth_query_params = {
    'response_type': 'code',
    'redirect_uri': SPOTIFY_REDIRECT_URI,
    'scope': SPOTIFY_SCOPES,
    'show_dialog': SPOTIFY_SHOW_DIALOG,
    'client_id': SPOTIFY_CLIENT_ID
}

@app.route('/login-spotify')
def spotify_login():
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in spotify_auth_query_params.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)

@app.route('/authorize_spotify')
def authorize_spotify():
    auth_token = request.args['code']
    code_payload = {
        'grant_type': 'authorization_code',
        'code': str(auth_token),
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data = code_payload)

    response_data = json.loads(post_request.text)
    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    token_type = response_data['token_type']
    expires_in = response_data['expires_in']

    authorization_header = {'Authorization': 'Bearer {}'.format(access_token)}

    markovified = session.get('markovified')

    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers = authorization_header)
    profile_data = json.loads(profile_response.text)
    return render_template('spotify.html', response_data = profile_data, strings = markovified)

@app.route('/spotify')
def spotify():
    return render_template('spotify.html')


if __name__ == '__main__':
    app.run(debug=True)