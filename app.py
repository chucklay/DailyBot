# Import statements
from __future__ import print_function
import smtplib
import dailybotdata
import datetime
import pyowm
import time
import re
from email.mime.text import MIMEText

import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

data = ''

def sendMsg(msg):
    global data
    strg = ''
    if(type(msg) is list):
        # This is a list of strings that must be sent. format and send.
        for item in msg:
            strg = strg + item + '\n'
    else:
        # This is a simple string that can be sent as-is.
        strg = msg

    # Format for email and send.
    SUBJECT = ''
    FROM = data['Sender']
    TO = data['Receiver']

    print(strg)

    # Get email client
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(data['Sender'], data['Password'])
    s.sendmail(data['Sender'], [data['Receiver']], strg)
    s.quit();
    return

def populateItinerary():
    # Gets daily events from google calendar.
    # First, authorize client. This is taken from Google's quickstart guide.

    global data
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    # Getting the upcoming 5 events
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, maxResults=5, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    eventStrs = ['You have the following events coming up:']

    if not events:
        return ['No upcoming events found.']
    for event in events:
        eventStrs.append(event['start'].get('dateTime', event['start'].get('date')) + " - " + event['summary']);
    return eventStrs;


def populateWeather():
    # Populates data to be sent in the message;
    # First, get the weather:
    global data
    msg = ''
    owm = pyowm.OWM(data['OWMKey'])
    fc = owm.daily_forecast(data['Location'], limit=1)
    f = fc.get_forecast()
    #print(f)
    for weather in f:
        temp = weather.get_temperature('fahrenheit')
        weath = weather.get_detailed_status()
        maxTmp = str(temp['max'])
	minTmp = str(temp['min'])
        msg = ('Good morning! Today\'s forecast calls for ' + weath +
        	   ' with a high of ' + maxTmp + ' and a low of ' + minTmp + '.')
    return msg

def main():
    global data
    data = dailybotdata.data
    print(data)
    print(type(data))
    wasSent = False                         # Checks if the program has executed
                                            # today. Resets between 1AM-3AM.
    while(True):
        # Main program execution loop.
        if(not wasSent):
            # Daily itinerary not sent. Get the current time
            # and check if now is an appropreate time to send.
            currentTime = datetime.datetime.now()
            print(currentTime.hour)
            if(currentTime.hour>5 and currentTime.hour<8):
                weather = populateWeather()
                #itinerary = populateItinerary()
                #sendMsg(itinerary)
		sendMsg(weather)
                wasSent = True
            else:
                # Not a good time. Sleep for 30 minutes.
		print('No data sent, but now is not the time. Sleeping...')
                time.sleep(60*30)
        else:
            # Message has been sent. Check to see if the current time is
            # between 1AM-3AM.
            currentTime = datetime.datetime.now()
            if(currentTime.hour>0 and currentTime.hour<4):
                wasSent = False
            else:
                print('Data has been sent today. Sleeping...')
                time.sleep(60*60)


if __name__ == '__main__':
    main()
