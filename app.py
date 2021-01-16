from flask import Flask, render_template, redirect, request, url_for, session
from decouple import config
from authlib.integrations.flask_client import OAuth, OAuthError

app = Flask(__name__)
app.secret_key = config('ACCESS_SECRET')
app.config.from_object('config')

if __name__ == '__main__':
    app.run(debug=True)