from app.config.settings import settings


class PromptBuilder:

    @staticmethod
    def build(question, chunks, max_context_chars=None):
        limit = max_context_chars if max_context_chars is not None else settings.MAX_CONTEXT_CHARS

        sections = []

        for index, chunk in enumerate(chunks, start=1):
            filename = chunk.get("filename") or "Unknown document"
            location = chunk.get("location")

            heading = f"[{index}] {filename}"
            if location:
                heading = f"{heading} - {location}"

            body = (chunk.get("content") or "").strip()

            sections.append(f"{heading}\n{body}")

        context = "\n\n".join(sections)

        if len(context) > limit:
            context = context[:limit].rsplit("\n", 1)[0]

        prompt = f"""You are an AI engineering assistant. Answer the question using only the numbered context below.

Rules:
1. Base every statement on the context and cite it inline as [1], [2], and so on.
2. The context may contain several documents about the same project; use them together when they clearly describe the same equipment or systems.
3. Do not invent specifications, equipment ratings, dimensions, safety limits, warranty terms, or code requirements.
4. If the context does not contain enough information to answer, reply exactly: The available knowledge base does not contain sufficient information.

Context:
{context}

Question: {question}

Answer:"""

        return prompt
