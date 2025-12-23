"""
Voice assistant main script.
Features:
- Listens for voice commands (or optional text fallback).
- Maps commands to actions: open websites/apps, tell time, search web, tell jokes, take notes, read Wikipedia, stop.
- Uses speech_recognition for voice -> text and pyttsx3 for TTS.
"""

import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import subprocess
import platform
import requests
import json
import time
import pyjokes
import wikipedia

from utils import speak, listen, parse_and_execute, ensure_voice_engine

# initialize TTS engine
engine = ensure_voice_engine()

WAKE_WORDS = ("assistant", "jarvis", "hey assistant", "hey jarvis")  # optional wake words

def main_loop():
    speak("Hello — I'm ready. Say a command or say 'exit' to stop.")
    while True:
        print("\nListening... (or type 'text:' to enter text input)")
        text = listen()  # listens and returns recognized text or None
        if not text:
            # fallback: allow keyboard input if recognition failed
            speak("I didn't catch that. You can type the command or say it again.")
            fallback = input("Type command (or press Enter to skip): ").strip()
            if fallback:
                text = fallback
            else:
                continue

        text = text.lower().strip()
        print("You said:", text)

        # immediate stop
        if text in ("exit", "quit", "stop", "goodbye"):
            speak("Goodbye. See you later.")
            break

        # optional wake word handling: if user used wake word, remove it
        for w in WAKE_WORDS:
            if text.startswith(w):
                text = text[len(w):].strip()

        handled = parse_and_execute(text, speak)
        if not handled:
            # last-resort: do a web search
            speak("I couldn't map that to a command. Shall I search the web for that?")
            # listening for yes/no
            ans = listen()
            if ans and "yes" in ans.lower():
                query = text
                url = f"https://www.google.com/search?q={requests.utils.requote_uri(query)}"
                speak(f"Searching the web for {query}")
                webbrowser.open(url)
            else:
                speak("Okay, command cancelled.")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        speak("Interrupted. Bye.")
    except Exception as e:
        print("Fatal error:", e)
        speak("An error occurred. Check the console for details.")

