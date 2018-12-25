# Button Social Network App
Twitter API Project for Button

About
------------
This is a web application that allows the user to search based on a few different criteria:

  1. Get all tweets by user id.
  2. Get all tweets of the authenticated user between two dates.
  3. Get all tweets matching a specified hash-tag
  
General User Requirements
------------
You will need a Twitter account for which to authenticate with. Also, some of the functions are limited in scope to
the account authenticated with, so a healthy amount of tweets is encouraged to search from!

Installation
------------
The application is currently hosted online at the following domain:

    http://button-env.cw5embfpkq.us-east-2.elasticbeanstalk.com/
    
Therefore, no local installation is necessary. However, if you would prefer to clone the repo and run it yourself, you can!

To do so, you will need to do the following:
  1. Clone the repo to a local directory.
  2. Create a python virtual environment with all requirements located in 'requirements.txt'.
  3. Modify the 'CALLBACK_URL' variable to use the localhost version as specified in the code comments.
  4. Run the Flask app on your local machine.

How to use
------------
After authenticating with the app, simply select any of the three search methods. Detailed descriptions below:

  1. Get all tweets by user id.
  
    - This endpoint will search all available tweets by a user id that you specify in the search bar.
    - Any handle in twitter can be used here. i.e "@realDonaldTrump"
    
  2. Get all tweets of the user between two dates.
  
    - A date range can be entered in form.
    - The dates MUST be of the following syntax separated by a hyphen: "MM/DD/YYYY HH:mm"
    - Example search term: "12/22/2018 00:00 - 12/24/2018 00:00"
    
  3. Get all tweets matching a hash-tag:
  
    - This will search all of twitter for tweets including the hash-tag.
    - Hashtags are entered in the normal syntax. i.e "#Trump"
    
Assumptions and Limitations
------------
- The original prompt stated that username searches were to be done by "connection".
Since all of Twitter is open to the user, this was assumed to mean all handles on Twitter.

- The Twitter API currently does not allow searching based on date ranges across the whole platform.
Therefore, the date range search functionality is limited to the user's timeline.

- The free tier of the Twitter API comes with data limitations of either 30 or 7 days depending on the API call.
These differences are marked in notes on the web application.

- Search results were limited to 100 tweets for performance reasons.

- Collections are used to organize search results for inspection later. It should be noted that if the app user
wishes not to keep these results, they should remove them after app use.
    
