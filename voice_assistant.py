from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pyttsx3
import speech_recognition as sr
import pytz
import subprocess

# Define the scope for Google Calendar API (read-only access)
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Constants for parsing user input
MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENSIONS = ["rd", "th", "st", "nd"]

# Function to convert text to speech
def speak(text):
    """
    Converts text to speech and speaks it out loud.
    """
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Function to capture audio input from the user
def get_audio():
    """
    Captures audio input from the microphone, converts it to text,
    and handles any recognition exceptions.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        user_input = ""

        try:
            user_input = recognizer.recognize_google(audio)
            print(user_input)
        except Exception as e:
            print("Error recognizing audio: " + str(e))

    return user_input.lower()

# Function to authenticate and connect to Google Calendar API
def authenticate_google():
    """
    Authenticates the user using Google Calendar API and returns a service object.
    """
    credentials = None

    # Load credentials from the token file if available
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token_file:
            credentials = pickle.load(token_file)

    # Refresh credentials or start OAuth flow if not valid
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("token.pickle", "wb") as token_file:
            pickle.dump(credentials, token_file)

    # Build the Google Calendar service
    calendar_service = build("calendar", "v3", credentials=credentials)
    return calendar_service

# Function to retrieve events from Google Calendar for a specific day
def get_events(day, calendar_service):
    """
    Retrieves events for a given day from Google Calendar and reads them aloud.
    """
    # Define start and end times for the day
    start_of_day = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_of_day = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc_timezone = pytz.UTC
    start_of_day = start_of_day.astimezone(utc_timezone)
    end_of_day = end_of_day.astimezone(utc_timezone)

    # Fetch events using Google Calendar API
    events_result = calendar_service.events().list(
        calendarId="primary",
        timeMin=start_of_day.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])

    # Speak out the events or inform if no events are found
    if not events:
        speak("You have no events scheduled for this day.")
    else:
        speak(f"You have {len(events)} events on this day.")
        for event in events:
            start_time = event["start"].get("dateTime", event["start"].get("date"))
            event_summary = event["summary"]

            # Extract time and format it
            start_hour = str(start_time.split("T")[1].split("-")[0])
            if int(start_hour.split(":")[0]) < 12:
                formatted_time = start_hour + " AM"
            else:
                formatted_time = str(int(start_hour.split(":")[0]) - 12) + ":" + start_hour.split(":")[1] + " PM"

            # Speak out the event details
            speak(f"{event_summary} at {formatted_time}")
            print(f"{start_time}: {event_summary}")

# Function to extract the date from user input
def get_date(text):
    """
    Parses the user input to identify a date and returns the appropriate datetime object.
    """
    today = datetime.date.today()

    # Handle the keyword 'today'
    if "today" in text:
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    # Loop through user input to identify months, days, and extensions
    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                if word.endswith(ext):
                    try:
                        day = int(word[:-len(ext)])
                    except:
                        pass

    # Adjust year and month for edge cases
    if month < today.month and month != -1:
        year += 1
    if month == -1 and day != -1:
        month = today.month + 1 if day < today.day else today.month

    # Calculate the exact day if only day of the week is mentioned
    if day_of_week != -1:
        current_day = today.weekday()
        day_difference = day_of_week - current_day
        if day_difference < 0:
            day_difference += 7
        if "next" in text:
            day_difference += 7
        return today + datetime.timedelta(day_difference)

    if day != -1:
        return datetime.date(year=year, month=month, day=day)

# Function to take notes
def make_note(note_text):
    """
    Writes the given text into a note file and opens it using Notepad.
    """
    current_time = datetime.datetime.now()
    file_name = f"{current_time.strftime('%Y-%m-%d_%H-%M-%S')}-note.txt"
    with open(file_name, "w") as note_file:
        note_file.write(note_text)

    subprocess.Popen(["notepad.exe", file_name])

# Wake word to activate the assistant
WAKE_WORD = "hey tim"

# Authenticate and initialize Google Calendar API service
calendar_service = authenticate_google()
print("Assistant initialized and ready...")

# Main loop to listen for user input
while True:
    user_input = get_audio()

    if WAKE_WORD in user_input:
        speak("I am ready.")
        user_input = get_audio()

        # Check for calendar-related commands
        CALENDAR_COMMANDS = ["what do i have", "do i have plans", "am i busy"]
        for command in CALENDAR_COMMANDS:
            if command in user_input:
                event_date = get_date(user_input)
                if event_date:
                    get_events(event_date, calendar_service)
                else:
                    speak("Sorry, I couldn't understand the date.")

        # Check for note-taking commands
        NOTE_COMMANDS = ["make a note", "write this down", "remember this"]
        for command in NOTE_COMMANDS:
            if command in user_input:
                speak("What would you like me to note down?")
                note_content = get_audio()
                make_note(note_content)
                speak("I've saved the note.")
