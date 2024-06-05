import speech_recognition as sr
import pyttsx3
from grq import GroqClient
from time import sleep, localtime
from datetime import date
from threading import Thread
import requests
import json
import datetime

with open("/home/vegapunk/Projects/MistralJarvis/sources/intents.json", "r") as json_file:
    intents = json.load(json_file)["intents"]

class PyttsxEngine():
    def __init__(self, voice_rate: int = 190, voice_volume: float = 1.5, female_voice: bool = None) -> None:
        self.voice_rate = voice_rate
        self.voice_volume = voice_volume
        self.voice = 1 if female_voice else 0
        self.engine = pyttsx3.init()
        self.set_property()

    def set_property(self):
        self.engine.setProperty("voice", self.engine.getProperty("voices")[self.voice].id)
        self.engine.setProperty("rate", self.voice_rate)
        self.engine.setProperty("volume", self.voice_volume)

    def tts(self, text: str) -> int:
        """This function return a text as an audio output."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except:
            print("Erreur dans lors de la lecture")
            return 1
        return 0
    
class Timer(Thread, PyttsxEngine):
    def __init__(self, seconds:int=0):
        Thread.__init__(self)
        PyttsxEngine.__init__(self)
        self._seconds = seconds
    
    def run(self):
        sleep(self._seconds)
        self.tts("ALARME")
        
class Alarm(Thread, PyttsxEngine):
    def __init__(self, hour:int, minute:int):

        try:
            assert 0 <= hour <= 23
            assert 0 <= minute <= 59

            PyttsxEngine.__init__(self)
            Thread.__init__(self)
            self._hour = hour
            self._min = minute
            self._is_active = True

        except AssertionError:
            print("Veuillez donner une heure valide")
    
    def switch_state(self):
        self._is_active = not self._is_active
    
    def run(self):
        while self._is_active:
            now = str(datetime.now()).split(" ")[1].split(":")
            if self._hour == int(now[0]) and self._min == int(now[1]) and self._is_active:
                self.tts("ALARME")
                self.switch_state()

class VocalAssistant(PyttsxEngine):
    def __init__(self, name: str = "Jarvis", city:str="Marseille", idx_microphone: int = 0, language: str = "fr-FR", **kargs) -> None:
        super().__init__(**kargs)
        self.name = name.lower()
        self.city = city
        self.Microphone = sr.Microphone(idx_microphone)
        self.language = language
        self.recognizer = sr.Recognizer()

    def date(self):
        months = {1:"Janvier", 2:"Février",3:"Mars",4:"Avril",
                  5:"Mai",6:"Juin",7:"Juillet",8:"Août",9:"Septembre",
                  10:"Octobre",11:"Novembre",12:"Décembre"}
        day = {1:"Lundi",2:"Mardi",3:"Mercredi",4:"Jeudi",5:"Vendredi",6:"Samedi",7:"Dimanche"}
        _date = f"{date.today().isoformat()}".split("-")
        return f"Nous sommes le {day[date.today().isoweekday()]} {_date[2]} {months[int(_date[1])]} {_date[0]}" 
    
    def time(self):
        return f"Il est actuellement {localtime().tm_hour}h{localtime().tm_min}"
    
    def timer(self, command:str):
        command = command.split(" ")
        sec = 0
        for idx, arg in enumerate(command):
            try :
                sec += 3600*int(command[idx-1]) if "heure" in arg else 0
                sec += 60*int(command[idx-1]) if "minute" in arg else 0
                sec += int(command[idx-1]) if "seconde" in arg else 0
            except:
                continue
        
        timer = Timer(sec)
        timer.start()
        self.tts("Lancement du minuteur")
        
    def alarm(self,command:str):
        command = command.split(" ")
        hour = 0
        min = 0
        try :
            for idx, arg in enumerate(command):
                if "heure" in arg:
                    hour = int(command[idx-1])
                    min = int(command[idx+1])
        except IndexError:
            pass
        alarm = Alarm(hour,min)
        alarm.start()
        self.tts("Activation de l'alarme")

    def weather(self, city:str):

        url_weather = f"http://api.openweathermap.org/data/2.5/weather?q={city}&APPID=beb97c1ce62559bba4e81e28de8be095"
        r_weather = requests.get(url_weather)
        data = r_weather.json()
        
        t_moy = data['main']['temp']-273.15
        t_min = data['main']['temp_min']-273.15
        t_max = data['main']['temp_max']-273.15
        temps = data['weather'][0]['description']
        return {"temp_moy":t_moy, "temp_min":t_min, "temp_max":t_max, "temps":temps}

    def run(self):
        print(f"{self.name.capitalize()} est prêt à vous écouter.")
        with self.Microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.energy_threshold = 500
            self.recognizer.pause_threshold = 0.7
            while True: 
                self.stt(source=source)


    def request_to_ia(self, query: str = None) -> str:
        response = GroqClient.request(query) if query else "Désolé, je n'ai pas compris ce que vous avez dit."
        return response

    def stt(self, source: sr.Microphone) -> None:
        print("En train d'écouter...", end="\r")

        audio = self.recognizer.listen(source, phrase_time_limit=7)

        try:
            text:str = self.recognizer.recognize_google(audio, language=self.language)
            print(f"Vous avez dit : {text}")

            if text.lower().startswith(self.name):
                print("Traitement de la requête...", end="\r")
                
                text = text.replace(self.name,"")
                action_done = False
                for intent in intents:
                    for pattern in intent["pattern"]:
                        if pattern in text.capitalize():
                            if intent["tag"] == "date":
                                self.tts(self.date())
                            elif intent["tag"] == "time":
                                self.tts(self.time())
                            elif intent["tag"] == "timer": 
                                self.timer(text)
                            elif intent["tag"] == "alarm":
                                self.alarm(text)
                            elif intent["tag"] == "weather":
                                meteo = self.weather(self.city)
                                self.tts(f"Aujourd'hui, il ferra en moyenne {meteo["temp_moy"]:.2f}. Au minimum il fera {meteo["temp_min"]:.2f} et au maximun {meteo["temp_max"]:.2f}")
                            
                            action_done = True 
                if not action_done:             
                    _response = self.request_to_ia(text)
                    print(f"{self.name.capitalize()} : {_response}")
                    self.tts(_response)
                else :
                    "Désolé, un problème est survenu, qu'elle était votre question ?"
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Erreur lors de la reconnaissance vocale : {e}")


if __name__ == "__main__":
    JARVIS = VocalAssistant(idx_microphone=0)
    JARVIS.run()
