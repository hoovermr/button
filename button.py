from flask import Flask, render_template, redirect, request, session
from datetime import datetime
from os import urandom
from time import sleep
import tweepy

application = Flask(__name__)
application.secret_key = urandom(24)

CONSUMER_KEY = 'GjJDCmivMndTR6WJ7gPi1EDhX'
CONSUMER_SECRET = 'nFRR3zTixaJbSOA6ik2Bp4jKWWCPsm0vMhflqVUWQDe1X2LLUx'
# CALLBACK_URL = 'http://button-env.cw5embfpkq.us-east-2.elasticbeanstalk.com/callback'
CALLBACK_URL = 'http://127.0.0.1:5000/callback'


@application.route('/')
def index():
    # No need to do auth if we have the correct token
    if session.get('access_token', None):
        return render_template('search_index.html')
    # First authorize the app and then the user
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET, CALLBACK_URL)
    try:
        redirect_url = auth.get_authorization_url()
    except tweepy.TweepError:
        print('Error! Failed to get request token.')
    return redirect(redirect_url)


@application.route('/callback')
def callback():
    # No need to do auth if we have the correct token
    if session.get('access_token', None):
        return render_template('search_index.html')

    if request.args.get("oauth_verifier"):
        verifier = request.args.get("oauth_verifier")
        token = request.args.get("oauth_token")

    # Re-build the auth handler and get the access token
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.request_token = {'oauth_token': token, 'oauth_token_secret': verifier}

    try:
        auth.get_access_token(verifier)
    except tweepy.TweepError:
        print('Error! Failed to get access token.')

    # Store access token and secret for the life of the user's session.
    session['access_token'] = auth.access_token
    session['access_secret'] = auth.access_token_secret

    return render_template('search_index.html')


@application.route('/conn_search.html', methods=['POST'])
def conn_search():
    # No access_token means session object is dead. Redirect to auth.
    if session.get('access_token', None) is None:
        return index()

    user_id = request.form['user_id']
    # Apply the access token and secret from session
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.access_token = session['access_token']
    auth.access_token_secret = session['access_secret']
    api = tweepy.API(auth)

    status_list = api.user_timeline(user_id)

    return render_template('conn_results.html',
                           status_list=status_list,
                           user_id=user_id)


@application.route('/date_search.html', methods=['POST'])
def date_search():
    # No access_token means session object is dead. Redirect to auth.
    if session.get('access_token', None) is None:
        return index()

    date = request.form['date']
    from_date_str, to_date_str = date.split(" - ")
    from_date = datetime.strptime(from_date_str, '%m/%d/%Y %H:%M')
    to_date = datetime.strptime(to_date_str, '%m/%d/%Y %H:%M')

    # Apply the access token and secret from session.
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.access_token = session['access_token']
    auth.access_token_secret = session['access_secret']
    api = tweepy.API(auth)

    tweets = []
    user_id = None
    # Page through all of the results. Limit to 100 tweets
    for tmp_tweet in limit_handled(tweepy.Cursor(api.user_timeline).items(100)):
        if user_id is None:
            user_id = tmp_tweet.user.screen_name
        if to_date > tmp_tweet.created_at > from_date:
            tweets.append(tmp_tweet)

    status = api.create_collection(name='Tweets:'+from_date_str+'-'+to_date_str)
    timeline_id = status.response['timeline_id']

    # Pack all the tweets into a collection. Limit to 100 tweets
    changes = []
    collection = {"id": timeline_id}
    for tweet in tweets:
        changes.append({"op": "add", "tweet_id": str(tweet.id)})
    collection['changes'] = changes[:100]

    kwargs = collection
    api.curate_collection(**kwargs)

    return render_template('date_results.html',
                           from_date_str=from_date_str,
                           to_date_str=to_date_str,
                           timeline_id=timeline_id,
                           user_id=user_id)


@application.route('/hash_search.html', methods=['POST'])
def hash_search():
    # No access_token means session object is dead. Redirect to auth.
    if session.get('access_token', None) is None:
        return index()

    hash_tag = request.form['hash_tag']
    # Apply the access token and secret from session
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.access_token = session['access_token']
    auth.access_token_secret = session['access_secret']
    api = tweepy.API(auth)

    status = api.create_collection(name='Tweets: '+hash_tag)
    timeline_id = status.response['timeline_id']
    # Extremely hacky way to get user_id.
    user_id = status.objects.get('users').get(list(status.objects.get('users').keys())[0]).get('screen_name')

    collection = {"id": timeline_id}
    changes = []

    # Page through all of the results. Limit to 6 pages and 100 tweets
    for result in limit_handled(tweepy.Cursor(api.search, q=hash_tag).pages(6)):
        for tweet in result:
            changes.append({"op": "add", "tweet_id": str(tweet.id)})
    collection['changes'] = changes[:100]

    kwargs = collection
    api.curate_collection(**kwargs)

    return render_template('hash_results.html',
                           hash_tag=hash_tag,
                           timeline_id=timeline_id,
                           user_id=user_id)


# Tweepy Cursor functions often throw 429 errors. Handle them here.
def limit_handled(cursor):
    while True:
        try:
            yield cursor.next()
        except tweepy.RateLimitError:
            sleep(15)


if __name__ == '__main__':
    application.run()
