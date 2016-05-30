# Import statements
import smtplib
import dailybotdata.py
import datetime
import pyowm
import time
from email.mime.text import MIMEText

from __future__ import print_function
import httplib2
import os

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def sendMsg(msg):
    strg = ''
    if(type(msg) is list):
        # This is a list of strings that must be sent. format and send.
        for(item in msg):
            strg = strg + item + '\n'
    else:
        # This is a simple string that can be sent as-is.
        strg = msg

    # Format for email and send.
    mimeStr = MIMEText(strg)
    mimeStr['Subject'] = ''
    mimeStr['From'] = data['Sender']
    mimeStr['To'] = data['Receiver']

    # Get email client
    s = smtplib.SMTP('localhost')
    s.sendmail(data['Sender'], [data['Receiver']], mimeStr.as_string())
    s.quit();
    return

def populateItinerary():
    # Gets daily events from google calendar.
    # First, authorize client. This is taken from Google's quickstart guide.

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
        eventStrs.append(event['summary']);
    return eventStrs;


def populateWeather():
    # Populates data to be sent in the message;
    # First, get the weather:
    try:
        owm = pywom.OWM(data['OWMKey'])
        fc = owm.daily_forecast(data['Location'], limit=1)
        f = fc.get_forecast()
        for(weather in f):
            temp = weather.get_temperature('fahrenheit')
            weath = weather.get_detailed_status()

            msg = 'Good morning! Today\'s forecast calls for ' + weath +
            ' with a high of ' + temp['temp_max'] + ' and a low of ' +
            weath['temp_min'] + '.'

            return msg;
    except Exception as e:
        print('Error getting weather:\n' + e)
        return 'Good morning! I was unable to get the weather today.'

def main():
    data = dailyBotData.data
    wasSent = False                         # Checks if the program has executed
                                            # today. Resets between 1AM-3AM.
    while(True):
        # Main program execution loop.
        if(!wasSent):
            # Daily itinerary not sent. Get the current time
            # and check if now is an appropreate time to send.
            currentTime = datetime.datetime.now()
            if(currentTime.hour > 5 && currentTime.hour < 6):
                weather = populateWeather()
                sendMsg(weather)
                itinerary = populateItinerary()
                sendMsg(itinerary);
                wasSent = True
            else:
                # Not a good time. Sleep for 30 minutes.
                time.sleep(60*30)
        else:
            # Message has been sent. Check to see if the current time is
            # between 1AM-3AM.
            currentTime = datetime.datetime.now()
            if(currentTime.hour > 1 && currentTime < 3):
                wasSent = False
            else:
                time.sleep(60*60)


if __name__ == '__main__':
    main()
