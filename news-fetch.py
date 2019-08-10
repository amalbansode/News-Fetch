 # 
 # NewsFetch - A Python script that fetches news items pertaining to a certain query.
 # 
 # ⓒ Amal Bansode, 2019.
 #

import requests
import json
import ssl
from datetime import datetime, timedelta
import os
import sys
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText

# Get a free access key from News API from https://newsapi.org/
# It's a simple two-minute process to sign up and get a free key!
# Enter the key below within the single quotes

API_KEY = 'YourNewsAPIKey' # News API Key
QUERY  = 'Tesla'
MAX_RESULTS = 25 # Maximum number of results needed. Must be <=100
BACK_DAYS = 7 # Number of past days from today to start searching from

# Email Settings
SEND_EMAIL = False # Send email using parameters below
SMTPserver = 'smtp.emailservices.com' # Find your email provider's SMTP server address and replace (Google is your best friend!)
SENDER = 'sender@email.com' # Sender email ID
DESTINATION = ['receiver@email.com'] # Receivers' email IDs
USER = 'sender-noreply@email.com' # Sender login username/email ID
PASS = 'password' # Sender login password. If you use 2FA, generate a token for this application and enter it here.
EMAILSUBJ = ('%s News Roundup (' + datetime.now().strftime('%Y-%m-%d') + ')') % (QUERY)

# Output file
OUTPUT_TO_FILE  = True # Output to a text file
FILENAME  = ('%s-News-%s.txt') % (QUERY, datetime.now().strftime('%Y-%m-%d'))

####################################
## DO NOT TOUCH BEYOND THIS POINT ##
####################################

if OUTPUT_TO_FILE:
    NOW = datetime.now()
    PATH = os.path.abspath(FILENAME).replace(FILENAME,'')
    F = open(PATH+FILENAME,'w')

# Date of day from one week ago in appropriate ISO-ish format
LAST_PERIOD = (datetime.now() - timedelta(BACK_DAYS)).strftime('%Y-%m-%d')

# Getting response from News API
URL = ('https://newsapi.org/v2/everything?q=%s&language=en&from=%s&sortBy=relevancy&apiKey=%s&pageSize=%s') % (QUERY, LAST_PERIOD, API_KEY, str(MAX_RESULTS))
RESPONSE = requests.get(URL)
PARSED_JSON = RESPONSE.json()
ARTICLE_LIST = PARSED_JSON["articles"]
NUM_ARTICLES = str(len(ARTICLE_LIST))

outStr = QUERY.upper() + ' NEWS FROM ' + LAST_PERIOD + ' TO TODAY (' + NUM_ARTICLES + ' articles)\n\n'

itemCount = 0
while itemCount < len(ARTICLE_LIST) and itemCount < MAX_RESULTS:
    currArticle = ARTICLE_LIST[itemCount]
    currArticleTitle = currArticle["title"]
    currArticleURL = currArticle["url"]
    outStr = outStr + ('\n' + currArticleTitle + '\n'+ currArticleURL + '\n\n')
    itemCount += 1

if OUTPUT_TO_FILE:
    F.write(("""\
        %s

——
Note: This action was performed by a computer and some irrelevant results may be included.
    """) % (outStr))
    F.close()

if SEND_EMAIL:
    text_subtype = 'plain'

    EMAILCONT = ("""\
        %s

——
Note: This action was performed by a computer and some irrelevant results may be included.
    """) % (outStr)
    try:
        msg = MIMEText(EMAILCONT, text_subtype)
        msg['Subject']= EMAILSUBJ
        msg['From']   = SENDER

        conn = SMTP(SMTPserver)
        conn.set_debuglevel(False) # Change to True if you are encountering repeated errors.
        conn.login(USER, PASS)
        try:
            conn.sendmail(SENDER, DESTINATION, msg.as_string())
        finally:
            print('Email sent successfully!')
            conn.quit()
    except:
        print('Sending failed :(')
        