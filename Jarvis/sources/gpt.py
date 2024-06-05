from os import getenv
import openai
from dotenv import load_dotenv; load_dotenv()
from openai.error import APIConnectionError

openai.api_key = getenv("OPENAI_KEY")
PROMPT = {"role":"system",
          "content":"Tu es un assistant personnel vocal nommé Jarvis. Imagine que tu es un assistant vocal comme Alexa ou Google Assistant. Réponds aux questions de manière courte, précise, simple et claire, en utilisant un langage naturel et conversationnel. N'hésite pas à utiliser des phrases complètes mais évite les longues explications inutiles. Essaie de répondre rapidement et de manière pertinente aux demandes de l'utilisateur."
          }

class AI():
    def __init__(self, prompt:dict, model:str="gpt-4-turbo") -> None:
        self._prompt =  prompt
        self._history = []
        self._model = model
        self.add_history(prompt)
        
    def add_history(self, entry:dict):
        self._history.append(entry)

    def request(self,content:str, retry:int=0) -> str:
        try:
            _request = {"role":"user","content":content}
            self.add_history(_request)
            _response =  openai.ChatCompletion.create(
                model = self._model,
                messages = self._history
            )
            return _response["choices"][0]["message"]["content"]
        except APIConnectionError:
            self.retry_request(content, retry=retry+1)

    def retry_request(self, content:str, attempt:int=0, limit:int=3):
        if not attempt >= limit:
            self.request(content, attempt)

ChatGPT = AI(prompt=PROMPT)