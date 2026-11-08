from langchain_ollama import ChatOllama

from app.config.settings import settings


class ChatService:

    def __init__(self):

        self.llm = ChatOllama(

            model=settings.LLM_MODEL,

            base_url=settings.OLLAMA_BASE_URL,

            temperature=0

        )

    def ask(self, prompt: str):

        response = self.llm.invoke(prompt)

        return response.content