from app.llm.chat import ChatService

from app.retrieval.prompts import PromptBuilder


class Generator:

    def __init__(self):

        self.chat = ChatService()

    def generate(

        self,

        question,

        chunks

    ):

        prompt = PromptBuilder.build(

            question,

            chunks

        )

        return self.chat.ask(

            prompt

        )