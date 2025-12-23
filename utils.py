import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import os
import subprocess
import platform
import pyjokes
import wikipedia

# === TTS ===
def ensure_voice_engine():
    engine = pyttsx3.init()
    # optional: tune voice rate and volume
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 10)
    vol = engine.getProperty('volume')
    engine.setProperty('volume', vol + 0.0)
    return engine

# engine must be created in main to avoid init issues on some OS, but expose speak that creates if missing.
_engine = None
def _get_engine():
    global _engine
    if _engine is None:
        _engine = ensure_voice_engine()
    return _engine

def speak(text):
    """Speak text aloud and print it."""
    print("Assistant:", text)
    engine = _get_engine()
    engine.say(text)
    engine.runAndWait()

# === Speech to text ===
def listen(timeout=5, phrase_time_limit=8):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=0.6)
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            text = r.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            # offline or network issue with Google API
            return None

# === Command parsing & execution ===
def parse_and_execute(text, speak_fn):
    """
    Map recognized text to actions.
    Returns True if command matched and executed, otherwise False.
    """
    text = text.lower()

    # greetings
    if any(g in text for g in ("hello", "hi", "hey")):
        speak_fn("Hello! How can I help you?")
        return True

    # time
    if "time" in text:
        now = datetime.datetime.now().strftime("%I:%M %p")
        speak_fn(f"The time is {now}")
        return True

    # open website
    if text.startswith("open "):
        target = text.replace("open ", "", 1).strip()
        # common mappings
        sites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://github.com",
            "gmail": "https://mail.google.com",
            "reddit": "https://www.reddit.com"
        }
        url = sites.get(target)
        if url is None:
            # if user said 'open stackoverflow.com' or 'open example dot com', try direct
            if "." in target or target.endswith("com"):
                url = "http://" + target if not target.startswith("http") else target
            else:
                # try search
                url = f"https://www.google.com/search?q={target.replace(' ', '+')}"
        speak_fn(f"Opening {target}")
        webbrowser.open(url)
        return True

    # search web
    if text.startswith("search ") or text.startswith("google "):
        query = text.split(" ", 1)[1]
        speak_fn(f"Searching for {query}")
        webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
        return True

    # wikipedia summary
    if text.startswith("wikipedia ") or text.startswith("who is ") or text.startswith("what is "):
        query = text.replace("wikipedia", "").replace("who is", "").replace("what is", "").strip()
        try:
            summary = wikipedia.summary(query, sentences=2)
            speak_fn(summary)
        except Exception:
            speak_fn("Sorry, I couldn't find that on Wikipedia.")
        return True

    # jokes
    if "joke" in text:
        j = pyjokes.get_joke()
        speak_fn(j)
        return True

    # notes
    if "take a note" in text or "note" in text:
        speak_fn("What should I write in the note?")
        note = listen()
        if not note:
            note = input("Type the note: ")
        with open("notes.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().isoformat()} - {note}\n")
        speak_fn("Note saved.")
        return True

    # open app (basic support, depends on OS)
    if text.startswith("launch ") or text.startswith("open app "):
        app_name = text.replace("launch", "").replace("open app", "").strip()
        speak_fn(f"Trying to open {app_name}")
        # Platform-specific attempts (simple)
        try:
            if platform.system() == "Windows":
                subprocess.Popen([app_name])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            else:  # Linux
                subprocess.Popen([app_name])
            speak_fn(f"{app_name} launched.")
        except Exception:
            speak_fn(f"Couldn't launch {app_name} — try giving the exact executable name.")
        return True

    # read notes
    if "read notes" in text or "show notes" in text:
        if os.path.exists("notes.txt"):
            with open("notes.txt", "r", encoding="utf-8") as f:
                content = f.read().strip()
            if content:
                speak_fn("Here are your notes.")
                print("\n--- NOTES ---\n", content)
                speak_fn(content[:500])  # speak first 500 chars to avoid long TTS
            else:
                speak_fn("Your notes file is empty.")
        else:
            speak_fn("You don't have any notes yet.")
        return True

    # fallback
    return False
