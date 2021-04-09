# Python libraries for Google Calendar API
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path
# Python libraries for time
from datetime import datetime, time, timedelta, date
from tkinter import messagebox

from pprint import pprint
"""
Reference: 
https://medium.com/pizzas/integrating-google-calendar-api-in-python-projects-ce74989cfaee
https://stackoverflow.com/questions/10048249/how-do-i-determine-if-current-time-is-within-a-specified-range-using-pythons-da
https://gist.github.com/cwurld/9b4e10dbeecab28345a3
"""

# NOTE: Adapted code from Medium artcle
def setup_gcal():
    """ Validates user's google account and returns service object """
    scopes = ['https://www.googleapis.com/auth/calendar']
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build("calendar", "v3", credentials=creds)
    return service

# NOTE: Adapted code from Medium Article
def create_event(start_time, end_time, description=None):
    """ Creates Google calendar with given datetime time objects """
    service = setup_gcal()
    # ! use settings to change timezone?
    timezone = 'America/Los_Angeles'
    if start_time == None or end_time == None:
        messagebox.showerror("Error", "Invalid time range")
        return 0
    event = {
        'summary': "TASK TIME", 
        'location': None,
        'description': description,
        'start': {
            'dateTime': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'timeZone': timezone,
        },
    }
    return service.events().insert(calendarId='primary', body=event).execute()

def schedule_time(check_start_time, check_end_time, time_duaration=7) -> dict:
    """ Returns dictionary of earliest available time within the next week """
    all_busy_events = get_busy_events()
    for d in range(1,time_duaration):
        # Increment by one day throughout the week
        check_day = datetime.today().date() + timedelta(d)
        if all_busy_events:
            # ! still something wrong
            is_day_free = []
            is_time_overlapping = False
            is_time_free = True
            for start,end in [event for event in all_busy_events if event[0].date() == check_day]:
                is_time_overlapping = is_time_between(check_start_time, check_end_time, start.time()) and is_time_between(check_start_time, check_end_time, end.time()) 
                is_time_free = not is_time_between(start.time(), end.time(), check_start_time) and not is_time_between(start.time(), end.time(), check_end_time) 
                is_day_free.append(is_time_free)
            if all(is_day_free) and not is_time_overlapping:
                appointment_start = datetime.combine(check_day, check_start_time)
                appointment_end = datetime.combine(check_day, check_end_time)
                return {"start": appointment_start, "end": appointment_end}
        else:
            # Schedule time for tomorrrow if no busy events within the next week
            return {"start": datetime.combine(check_day, check_start_time), "end": datetime.combine(check_day, check_end_time)}

# NOTE: Adapted code from StackOverflow
def is_time_between(start_time, end_time, check_time=None):
    # If check time is not given, default to current time
    check_time = datetime.now().time() if not check_time else check_time
    if start_time < end_time:
        return check_time >= start_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= start_time or check_time <= end_time

def get_calendarIDs() -> list:
    service = setup_gcal()
    calendars = service.calendarList().list().execute()
    if not calendars:
        return []
    all_ids = [ids["id"] for ids in calendars["items"]]
    return all_ids

# NOTE: Adapted code from Github
def get_busy_events() -> list:
    service = setup_gcal()
    all_ids = get_calendarIDs()
    # Get events for this whole week
    now = datetime.utcnow().isoformat() + 'Z'
    end = (datetime.utcnow() + timedelta(days=7)).isoformat() + 'Z'
    all_events = []
    for calendarId in all_ids:
        # Iterature through all calendars
        events_result = service.events().list(calendarId=calendarId, timeMin=now,
                                            timeMax=end, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        all_events.append(events)
    # Flatten to 1-D list
    all_events = [j for sub in all_events for j in sub]
    all_times = {}
    if not all_events:
        return []
    for event in all_events:
        if "date" in event["start"] or "date" in event["end"]: continue
        # Convert to datetime objects
        start = event["start"]["dateTime"][:-(len("-6:00")+1)]
        end = event["end"]["dateTime"][:-(len("-6:00")+1)]
        all_times[start] = end

    # Sort from earliest start datetime to latest
    ordered_times = sorted(filter(lambda x: len(x[0])==19, all_times.items()), key = lambda x:datetime.strptime(x[0], "%Y-%m-%dT%H:%M:%S"))
    pprint(ordered_times)
    return [(datetime.strptime(start, "%Y-%m-%dT%H:%M:%S"), datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")) for start,end in ordered_times]
