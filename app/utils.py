import os
from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def load_documents(file_path: str):
    """Load and split documents from a text file."""
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    return splitter.create_documents([text])


def create_vector_store(documents):
    """Embed documents and create a FAISS vector store."""
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.from_documents(documents, embedding_model)


def create_qa_chain(vector_store):
    """Create a RetrievalQA chain with Gemini as the LLM."""
    retriever = vector_store.as_retriever(search_type="similarity", k=4)

    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )


def ask_rag(question: str, qa_chain):
    """Ask a question using the RAG pipeline."""
    response = qa_chain.invoke({"query": question})
    return response["result"].strip()


if __name__ == "__main__":
    file_path = "scrapped_pages/combined_scrape.txt"

    docs = load_documents(file_path)
    vector_store = create_vector_store(docs)
    qa_chain = create_qa_chain(vector_store)

    answer = ask_rag("What is Ameotech?", qa_chain)
    print("Answer:", answer)
