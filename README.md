# Local-Rag-System

Here is a breakdown of the technical stack I've selected to ensure a robust and privacy-focused application:
Ingestion & Orchestration: I've included both LangChain and LlamaIndex, giving you flexibility in how you manage the data pipeline. For specific file types, I've mapped out specialized libraries: PyPDF2 for PDFs, python-docx for Word documents, Pandas for structured CSV/Excel data, and Tesseract OCR for processing screenshots. 

Storage Layer: I've separated the datastore conceptually. ChromaDB serves as the vector store for fast semantic search, while PostgreSQL handles the operational metadata. 

Local AI (Ollama): Both embedding generation and response generation are routed through a local Ollama instance (configured here with Mistral 7B). This ensures no data leaves your environment. 

Evaluation & UI: I have added the Ragas framework to handle the response evaluation and a user interface layer using Streamlit or Chainlit for the interaction

<img width="1559" height="688" alt="System-Architecture" src="https://github.com/user-attachments/assets/1a75f853-c568-4d88-b132-7e08b4dcbe3b" />
