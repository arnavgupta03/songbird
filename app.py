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

@app.errorhandler(OAuthError)
def handle_error(error):
    return render_template('error.html', error=error)

@app.route('/')
def homepage():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/login')
def login():
    redirect_uri = 'http://song-bird-web-app.herokuapp.com/authorize'
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

SPOTIFY_REDIRECT_URI = 'http://song-bird-web-app.herokuapp.com/authorize_spotify'
SPOTIFY_SCOPES = 'user-top-read playlist-modify-private playlist-modify-public'
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

    session.pop('token', None)
    session.pop('user', None)

    markovified = session.get('markovified')

    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers = authorization_header)
    profile_data = json.loads(profile_response.text)
    #session['profile_data'] = profile_data['uri'][13:]

    personalization_api_endpoint = "{}/me/top/artists".format(SPOTIFY_API_URL)
    personalization_params = {
        'time_range': 'long_term',
        'limit': '50',
    }
    personalization_response = requests.get(personalization_api_endpoint, headers = authorization_header, params = personalization_params)
    personalization_data = json.loads(personalization_response.text)
    #session['personalization_data'] = personalization_data

    user_id = profile_data['uri'][13:]

    create_playlist_api_endpoint = "{}/users/{}/playlists".format(SPOTIFY_API_URL, user_id)
    create_playlist_params = json.dumps({
        'name': markovified,
        'description': 'Generated by Songbird, based on your Timeline'
    })
    create_playlist_response = requests.post(create_playlist_api_endpoint, data = create_playlist_params, headers = authorization_header)
    create_playlist_data = json.loads(create_playlist_response.text)
    playlist_uri = create_playlist_data['uri'][17:]

    song_counter = 0
    song_search_api_endpoint = "{}/search".format(SPOTIFY_API_URL)

    songs = []

    for word in markovified.split(' '):
        song_search_params = {
            'q': word,
            'type': 'track',
            'limit': '1',
        }
        song_search_response = requests.get(song_search_api_endpoint, headers = authorization_header, params = song_search_params)
        song_search_data = json.loads(song_search_response.text)
        #session['word'] = word
        if len(song_search_data['tracks']['items']) > 0:
            track_uri = song_search_data['tracks']['items'][0]['uri']
            #session['track_uri'] = track_uri
            songs.append(track_uri)
    #session['track_uri'] = songs

    add_playlist_api_endpoint = "{}/playlists/{}/tracks".format(SPOTIFY_API_URL, playlist_uri)
    add_playlist_params = json.dumps({
        'uris': songs
    })
    add_playlist_response = requests.post(add_playlist_api_endpoint, data = add_playlist_params, headers = authorization_header)
    add_playlist_data = json.loads(add_playlist_response.text)
    #session['add_playlist'] = add_playlist_data

    session['playlist_url'] = "https://open.spotify.com/embed/playlist/" + playlist_uri

    return redirect('spotify')
    #return render_template('spotify.html', strings = markovified)
    #return render_template('spotify-debug.html', response_data = profile_data, strings = markovified, headerstring = personalization_data)

@app.route('/spotify')
def spotify():
    markovified = session.get('markovified')
    #track_uri = session.get('add_playlist')
    #word = session.get('word')
    playlist_url = session.get('playlist_url')
    return render_template('spotify.html', strings = markovified, playlist_url = playlist_url)


if __name__ == '__main__':
    app.run(debug=True)