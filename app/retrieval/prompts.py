class PromptBuilder:

    @staticmethod
    def build(

        question,

        chunks

    ):

        context = ""

        for item in chunks:

            context += item["content"]

            context += "\n\n"

        prompt = f"""

You are an AI assistant.

Answer ONLY using the provided context.

If the answer is not contained inside the context,

reply exactly:

I don't know.

------------------------

Context

{context}

------------------------

Question

{question}

Answer

"""

        return prompt