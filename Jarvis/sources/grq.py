import os
from dotenv import load_dotenv; load_dotenv()
from groq import Groq, APIConnectionError

class AI():
    def __init__(self, _ApiKey:str, _prompt:dict, _model:str="mixtral-8x7b-32768") -> None:
        self._GroqClient = Groq(api_key=_ApiKey)
        self._model = _model
        self._prompt = _prompt
        self._history = []
        self.history(_prompt)
    
    def history(self, entry:dict):
        self._history.append(entry)
        
    def request(self, content:str, retry:int=0) -> str:
        try:
            _request = {"role":"user",
                        "content":content}
            self.history(_request)
            _response = self._GroqClient.chat.completions.create(
                model=self._model,
                messages=self._history
            )
            return _response.choices[0].message.content
        except APIConnectionError:
            print("Error")
            self.retry_request(content, retry=retry+1)
    
    def retry_request(self, content:str, attempt:int=0, limit:int=3):
        if not attempt >= limit:
            self.request(content, attempt)
            
PROMPT = {"role":"system",
          "content":"Tu es un assistant personnel vocal nommé Jarvis. Imagine que tu es un assistant vocal comme Alexa ou Google Assistant. Réponds aux questions de manière courte, précise, simple et claire, en utilisant un langage naturel et conversationnel. N'hésite pas à utiliser des phrases complètes mais évite les longues explications inutiles. Essaie de répondre rapidement et de manière pertinente aux demandes de l'utilisateur."
          }
GroqClient = AI(_ApiKey=os.getenv("GROQ_API_KEY"), _prompt=PROMPT)
        

