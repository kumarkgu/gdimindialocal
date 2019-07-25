import soundcard as sc
import pyttsx3 as ptxs
import win32com.client as wincli


def first_code():
    speakers = sc.all_speakers()
    defspeaker = sc.default_speaker()
    print(speakers)
    print(defspeaker)


def first_text_to_speech():
    engine = ptxs.init()
    engine.say("Good Morning!! Gunjan")
    engine.runAndWait()


def windows_ttspeech():
    speak = wincli.Dispatch("SAPI.SpVoice")
    text = "I am!!! Gunjan"
    speak.Speak(text)


windows_ttspeech()
# first_code()
# first_text_to_speech()
