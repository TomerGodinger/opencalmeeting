# opencalmeeting.py
# A small utility for opening the Zoom meeting on your current- or
# next-scheduled calendar event.
# 
# NOTE: Written for Linux (Ubuntu), but in order to support other operating
# systems you only need to replace the contents of the os.system() calls in
# the open_link(), show_error() and show_notification() functions to the
# equivalent commands for your system.

import datetime
import os.path
import re
import os
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def open_link(url):
    os.system(f"xdg-open \"{url}\"")

def show_error(msg):
    os.system(f"zenity --error --no-wrap --title \"Open Calendar Meeting\" --text \"{msg}\"")

def show_notification(msg):
    os.system(f'notify-send --hint int:transient:1 "Open Calendar Meeting" "{msg}"')

def main(index):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=index + 1, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events or len(events) == 0:
            show_error('No events found.')
            return
        # https://www.google.com/url?q=https://redis.zoom.us/j/98489572581?pwd%3DTDBXVjZldFBoeTlYTGh3cXZ2R3VEZz09&sa=D&source=calendar&ust=1648195824226050&usg=AOvVaw00JYwDLdRC-6oMJNMDS9HX
        meeting_link = None
        event = events[index]
        event_text = str(event)
        p = re.compile(r"'https://[^\.]*\.zoom\.us/j/(\d+)\?pwd(=|%3D)([0-9a-zA-Z]+)'")
        result = p.search(event_text)
        if result:
            confno = result.group(1)
            password = result.group(3)
            meeting_link = f"zoommtg://redislabs.zoom.us/join?confno={confno}&pwd={password}&action=join"
            show_notification(f"Opening meeting: {event['summary']}")
            # open_link(meeting_link)
        else:
            show_error('No event found with meeting link.')

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    index = 0
    if len(sys.argv) > 1:
        try:
            index = max(0, int(sys.argv[1]))
        except:
            pass
    
    main(index)
