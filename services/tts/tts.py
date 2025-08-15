import sys
import pyttsx3

def speak(text: str):
    """Initializes TTS engine and speaks the given text."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    # Allows running this script directly from the command line for testing
    msg = " ".join(sys.argv[1:]) or "Hello from your local AI assistant."
    speak(msg)