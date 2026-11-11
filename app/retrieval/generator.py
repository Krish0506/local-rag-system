from app.config.settings import settings

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
            chunks,
            max_context_chars=settings.MAX_CONTEXT_CHARS,
        )

        return self.chat.ask(
            prompt
        )