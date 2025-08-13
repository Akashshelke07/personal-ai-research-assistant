# services/tts/tts.py
import sys
import pyttsx3

def speak(text: str):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "Hello from your local AI assistant."
    speak(msg)
