from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

model = init_chat_model('gpt-5-nano')

response = model.invoke("What is India Doing in Quantum Computing Space?")

print(response.content)