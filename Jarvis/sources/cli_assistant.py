from time import sleep, localtime
from datetime import date, time, datetime
from threading import Thread
from grq import GroqClient
import json
import requests

with open("/home/vegapunk/Projects/MistralJarvis/sources/intents.json", "r") as json_file:
    intents = json.load(json_file)["intents"]

class Alarm(Thread):
    def __init__(self, hour:int, minute:int):

        try:
            assert 0 <= hour <= 23
            assert 0 <= minute <= 59

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
                print("ALARM", end="\n")
                self.switch_state()

class Timer(Thread):
    def __init__(self, seconds:int=0):
        Thread.__init__(self)
        self._seconds = seconds
    
    def run(self):
        sleep(self._seconds)
        print("ALARM", end="\n")
        

class CLI_Assistant():
    def __init__(self) -> None:
        pass
    
    def time(self):
        return f"Il est actuellement {localtime().tm_hour}h{localtime().tm_min:02d}"

    def date(self):
        months = {1:"Janvier", 2:"Février",3:"Mars",4:"Avril",
                  5:"Mai",6:"Juin",7:"Juillet",8:"Août",9:"Septembre",
                  10:"Octobre",11:"Novembre",12:"Décembre"}
        day = {1:"Lundi",2:"Mardi",3:"Mercredi",4:"Jeudi",5:"Vendredi",6:"Samedi",7:"Dimanche"}
        _date = f"{date.today().isoformat()}".split("-")
        return f"Nous sommes le {day[date.today().isoweekday()]} {_date[2]} {months[int(_date[1])]} {_date[0]}"
    
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
        print("Lancement du minuteur")

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
        print("Activation de l'alarme")
    
    def weather(self, city:str="Marseille"):

        url_weather = f"http://api.openweathermap.org/data/2.5/weather?q={city}&APPID=beb97c1ce62559bba4e81e28de8be095"
        r_weather = requests.get(url_weather)
        data = r_weather.json()
        
        t_moy = data['main']['temp']-273.15
        t_min = data['main']['temp_min']-273.15
        t_max = data['main']['temp_max']-273.15
        temps = data['weather'][0]['description']
        return {"temp_moy":t_moy, "temp_min":t_min, "temp_max":t_max, "temps":temps}
        
    def run(self):
        while True:
            command = input("Enter command : ")

            action_done = False
            for intent in intents:
                for pattern in intent["pattern"]:
                    if pattern in command.capitalize():
                        if intent["tag"] == "time":
                            print(self.time())
                        elif intent["tag"] == "date":
                            print(self.date())
                        elif intent["tag"] == "timer":
                            self.timer(command=command)
                        elif intent["tag"] == "alarm":
                            self.alarm(command=command)
                        elif intent["tag"] == "weather":
                            temp = self.weather()
                            print(f"Météo : {temp['temps']}")
                            print(f"Température moyenne : {temp['temp_moy']:.2f}")
                            print(f"Température minimum : {temp['temp_min']:.2f}")
                            print(f"Température maximale : {temp['temp_max']:.2f}")
                        action_done = True

            if not action_done and command:
                print(GroqClient.request(command))
    
            

if __name__ == "__main__":
    CLI_Assistant().run()

