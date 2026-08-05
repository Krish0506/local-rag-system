from app.retrieval.generator import Generator
from app.retrieval.retriever import Retriever


def main():

    retriever = Retriever()

    generator = Generator()

    print()

    print("Local RAG Chat")

    print("----------------------")

    while True:

        question = input("\nQuestion: ")

        if question.lower() == "exit":

            break

        chunks = retriever.retrieve(

            question

        )

        answer = generator.generate(

            question,

            chunks

        )

        print()

        print(answer)


if __name__ == "__main__":

    main()