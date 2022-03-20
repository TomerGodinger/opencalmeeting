# opencalmeeting
A small utility for opening the Zoom meeting on your current- or
next-scheduled calendar event.

Based on example code from Google [here](https://developers.google.com/calendar/api/quickstart/python).

In order to use this, you need to:
1. Set up a project with OAuth credentials for a desktop app as described [here](https://developers.google.com/workspace/guides/create-credentials).
2. Enable the Google Calendar API for it.
3. Add yourself (the user whose calendar you wish to access) as a test user
(or make the project public and go through the process of verifying it -
I haven't done that so I don't know what that entails).
4. Follow the instructions on the above link under "OAuth client ID credentials" (make sure to select "Desktop app" tab in there) to create and download the
"credentials.json" file this program needs.
5. Run the program. The first time you do, a browser window should open asking you to give the program access to your calendar. After that your user token will be saved in a file so you will no longer need to go through that process.

## Note about Operating System Support
This was written for Linux (Ubuntu), but in order to support other operating
systems you only need to replace the contents of the `os.system()` calls in
the `open_link()`, `show_error()` and `show_notification()` functions to the
equivalent commands for your system.

For example, on a Mac, in order to open the meeting itself in `open_link()`, instead of the current code:
```py
os.system(f"xdg-open \"{url}\"")
```
you should change it to:
```py
os.system(f"open \"{url}\"")
```

Might be a good idea to add automatic detection of the OS. Haven't done that.
