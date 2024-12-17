# Install required libraries
!pip install gTTS

from gtts import gTTS
from datetime import datetime
from IPython.display import Audio, display
import os

def speak(text):
    """Convert text to speech and play it."""
    tts = gTTS(text=text, lang='en')
    tts.save("/content/response.mp3")
    display(Audio("/content/response.mp3", autoplay=True))

def main():
    speak("Hello! I am your voice assistant. How can I help you?")
    while True:
        # Simulate listening by taking input from the user
        command = input("Type your command (e.g., hello, time, exit): ").lower()

        if command:
            if "hello" in command:
                speak("Hi there! Nice to meet you.")
            elif "time" in command:
                now = datetime.now().strftime("%H:%M:%S")
                speak(f"The current time is {now}")
            elif "date" in command:
                today = datetime.now().strftime("%A, %B %d, %Y")
                speak(f"Today's date is {today}")
            elif "exit" in command or "bye" in command:
                speak("Goodbye! Have a great day!")
                break
            else:
                speak("I'm sorry, I don't understand that. Could you try again?")

# Run the assistant
main()
