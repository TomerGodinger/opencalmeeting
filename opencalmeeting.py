# opencalmeeting.py
# A small utility for opening the Zoom meeting on your current- or
# next-scheduled calendar event.
# 
# Based on example code from Google taken from here:
# https://developers.google.com/calendar/api/quickstart/python
# 
# In order to use this, you need to set up a project with OAuth credentials
# for a desktop app as described here:
# https://developers.google.com/workspace/guides/create-credentials
# You'll also need to enable the Google Calendar API for it.
# Add yourself (the user whose calendar you wish to access) as a test user
# (or make the project public and go through the process of verifying it -
# I haven't done that so I don't know what that entails) and follow the
# instructions on the above link under "OAuth client ID credentials" (make
# sure to select "Desktop app" tab in there) to create and download the
# "credentials.json" file this program needs, then run the program. The
# first time you do, a browser window should open asking you to give the
# program access to your calendar. After that your user token will be saved
# in a file so you will no longer need to go through that process.
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



def open_link(url: str):
    """Opens a URL via a system command. Very OS-specific."""
    
    os.system(f"xdg-open \"{url}\"")


def show_error(msg: str):
    """Shows an error message box via a system command. Very OS-specific."""

    os.system(f"zenity --error --no-wrap --title \"Open Calendar Meeting\" --text \"{msg}\"")


def show_notification(msg: str):
    """Shows a pop-up notification via a system command. Very OS-specific."""

    os.system(f'notify-send --hint int:transient:1 "Open Calendar Meeting" "{msg}"')


def main(index: int):
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
        
        # Attempt to extract the meeting link from the desired event
        meeting_link = None  # type: str
        event = events[index]
        event_text = str(event)
        p = re.compile(r"https://(?P<url>[^\.]*\.zoom\.us)/j/(?P<confno>\d+)(?:\?pwd(?:=|%3D)(?P<password>[0-9a-zA-Z]+))?")
        result = p.search(event_text)
        if result:
            # If successful, extract the meeting URL, identifier and password 
            baseurl = result.group('url')
            confno = result.group('confno')
            password = result.group('password')
            
            # Create the full link for opening the Zoom meeting
            meeting_link = f"zoommtg://{baseurl}/join?confno={confno}&action=join"
            if password:
                meeting_link += f"&pwd={password}"

            # Specify which event we're opening (if there's an issue and a
            # different event is found, we want the user to see that something
            # is wrong, rather than wait in the wrong meeting room) and open it
            show_notification(f"Opening meeting: {event['summary']}")
            open_link(meeting_link)
        else:
            # We found events, but they didn't have a Zoom meeting link in a
            # format we know
            show_error('No event found with meeting link.')

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    index = 0
    if len(sys.argv) > 1:
        # Added some minimal value enforcement here but it's not meant to
        # cover every wrong argument value, so please use this properly
        try:
            index = max(0, int(sys.argv[1]))
        except:
            pass
    
    main(index)
