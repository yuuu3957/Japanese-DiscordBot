import os
from groq import Groq
import getpass

def set_groq_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}:")

def start_groq() :
    set_groq_env ("Groq_API_KEY")
    client = Groq()
    model = "llama-3.3-70b-versatile"
    return model, client