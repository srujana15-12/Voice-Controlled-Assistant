1)Create a virtual environment:
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
2)Make sure microphone access works:

On Windows, allow microphone permission for terminal/Python.

If pyaudio fails to install, use pipwin install pyaudio (Windows) or install portaudio19-dev on Linux.
3)RUN
python main.py

4)Speak commands like:

"What is the time?"

"Open YouTube"

"Search machine learning"

"Tell me a joke"

"Take a note"

"Read notes"

"Exit"