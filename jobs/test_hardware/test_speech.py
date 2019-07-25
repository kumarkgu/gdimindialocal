import speech_recognition as sr
import pyaudio as pa


def check_audio():
    paudio = pa.PyAudio()
    for idx in range(0, paudio.get_device_count()):
        devinfo = paudio.get_device_info_by_index(idx)
        if str(devinfo["name"]) == "Microphone (Jabra Link 370)":
            print(devinfo)


def speech_test():
    robj = sr.Recognizer()
    istimeout = 0
    with sr.Microphone(device_index=1) as source:
        try:
            audio = robj.listen(source=source, timeout=5)
        except sr.WaitTimeoutError:
            print("No Sound coming")
            istimeout = 1
    if istimeout == 0:
        try:
            text_us = robj.recognize_google(audio_data=audio, language='en-US')
            text_in = robj.recognize_google(audio_data=audio, language='en-IN')
            print("You said (US): {}".format(text_us))
            print("You said (IN): {}".format(text_in))
        except LookupError:
            print("Could not understand Audio")


def list_microphone():
    for idx, micname in enumerate(sr.Microphone.list_microphone_names()):
        print("Index: {}. Name is: {}".format(str(idx), micname))


# check_audio()
speech_test()
# list_microphone()

# {'index': 1, 'structVersion': 2, 'name': 'Microphone (Jabra Link 370)', 'hostApi': 0, 'maxInputChannels': 1, 'maxOutputChannels': 0, 'defaultLowInputLatency': 0.09, 'defaultLowOutputLatency': 0.09, 'defaultHighInputLatency': 0.18, 'defaultHighOutputLatency': 0.18, 'defaultSampleRate': 44100.0}
# {'index': 7, 'structVersion': 2, 'name': 'Microphone (Jabra Link 370)', 'hostApi': 1, 'maxInputChannels': 1, 'maxOutputChannels': 0, 'defaultLowInputLatency': 0.12, 'defaultLowOutputLatency': 0.0, 'defaultHighInputLatency': 0.24, 'defaultHighOutputLatency': 0.0, 'defaultSampleRate': 44100.0}
# {'index': 14, 'structVersion': 2, 'name': 'Microphone (Jabra Link 370)', 'hostApi': 3, 'maxInputChannels': 1, 'maxOutputChannels': 0, 'defaultLowInputLatency': 0.003, 'defaultLowOutputLatency': 0.0, 'defaultHighInputLatency': 0.01, 'defaultHighOutputLatency': 0.0, 'defaultSampleRate': 16000.0}
# {'index': 21, 'structVersion': 2, 'name': 'Microphone (Jabra Link 370)', 'hostApi': 4, 'maxInputChannels': 1, 'maxOutputChannels': 0, 'defaultLowInputLatency': 0.01, 'defaultLowOutputLatency': 0.01, 'defaultHighInputLatency': 0.08533333333333333, 'defaultHighOutputLatency': 0.08533333333333333, 'defaultSampleRate': 16000.0}