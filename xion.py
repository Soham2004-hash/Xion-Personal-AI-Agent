import os
import subprocess
import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser

TODAYS_SCHEDULE = (
    "Here is your schedule for today: "
    "First, Clone the preexisting repository of Micro Expression Recognition Test Files. "
    "Second, Unbound all the files from the folders .. "
    "Third, Update the protocol_loader file. "
    "Finally, Update the protocol_loader as subject wise if you need you can see the screenshot which you have taken yesterday."
)

engine = pyttsx3.init()

voice_id = "com.apple.voice.enhanced.en-GB.Daniel"  
try:
    engine.setProperty('voice', voice_id)
except:
    pass 

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    greeting = ""

    if hour >= 6 and hour < 12:
        greeting = "Good Morning!"
    elif hour >= 12 and hour < 18:
        greeting = "Good Afternoon!"
    elif hour >= 18 and hour < 20:
        greeting = "Good Evening!"
    else:
        greeting = "It is your appropriate working time!"

    intro = f"Welcome back sir. {greeting} This is Xion, your personal assistant.{TODAYS_SCHEDULE}"
    
    speak(intro)
    speak("...How may I help you now?")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        print("Say that again please...")  
        return "None"
    return query

if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand().lower()

        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            try:
                results = wikipedia.summary(query, sentences=2) 
                speak("According to Wikipedia")
                print(results)
                speak(results)
            except:
                speak("I couldn't find anything on Wikipedia for that.")

        elif 'open youtube' in query:
            speak("Opening YouTube") 
            webbrowser.open("https://www.youtube.com") 
        
        elif 'open github' in query:
            speak("Opening your GitHub")
            webbrowser.open("https://github.com/Soham2004-hash")

        elif 'open database' in query:
            speak("Opening Kaggle for you sir")
            webbrowser.open("https://www.kaggle.com/work")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, The time is : {strTime}")
            print(strTime)

        elif 'open code' in query or 'open vs code' in query:
            speak("Opening Visual Studio Code")
            try:
                subprocess.run(["open", "-a", "Visual Studio Code"])
            except FileNotFoundError:
                speak("I could not find Visual Studio Code.")

        elif 'open spotify' in query or 'play music' in query:
            speak("Opening Spotify...")
            try:
                subprocess.run(["open", "-a", "Spotify"])
            except FileNotFoundError:
                speak("I could not find Spotify.")

        elif 'open brave' in query or 'open browser' in query:
            speak("Opening Brave Browser")
            try:
                subprocess.run(["open", "-a", "Brave Browser"])
            except FileNotFoundError:
                speak("I could not find Brave Browser.")

        elif 'stop' in query or 'exit' in query:
            speak("Goodbye sir. Have a nice day.")
            break