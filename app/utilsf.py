import os
import re
from urllib.parse import urljoin,urlparse
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Directory constants
VECTOR_STORE_DIR = "vetorstore"
TEMP_DIR = "temp"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

SCRAPED_DATA_DIR = "scraped_data"
os.makedirs(SCRAPED_DATA_DIR, exist_ok=True)


def sanitize_filename(path):
    """
    Sanitize a URL path to create a safe filename by replacing unsafe characters.

    Args:
        path (str): A relative or absolute URL path.

    Returns:
        str: A filename-safe string.
    """
    if not path or path in ['/', '#']:
        return "index"
    path = path.strip().replace('/', '_').replace('\\', '_')
    path = re.sub(r'[^a-zA-Z0-9._-]', '_', path)
    return path or "index"

def scrape_website(base_url: str, client_name: str) -> list[dict]:
    """
    Scrape internal links from base_url, extract visible text, and save combined text to client's folder.

    Args:
        base_url (str): The URL to scrape.
        client_name (str): The name of the client (used for folder structure).

    Returns:
        list[dict]: A list of {'url': ..., 'text': ...} entries.
    """
    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            print(f"Failed to load base URL: {base_url}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all('a', href=True)

        base_domain = urlparse(base_url).netloc
        hrefs = set()

        for link in links:
            href = link['href']
            if href.startswith('#'):
                continue
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == base_domain:
                hrefs.add(full_url)

        scraped_texts = []
        combined_text = ""

        client_folder = os.path.join(SCRAPED_DATA_DIR, client_name)
        os.makedirs(client_folder, exist_ok=True)
        file_path = os.path.join(client_folder, "combined_scrape.txt")

        for url in hrefs:
            try:
                page_response = requests.get(url)
                if page_response.status_code == 200:
                    page_soup = BeautifulSoup(page_response.text, "html.parser")
                    page_text = page_soup.get_text(separator="\n", strip=True)

                    combined_text += f"\n\n===== {url} =====\n\n{page_text}"
                    scraped_texts.append({'url': url, 'text': page_text})
                    print(f"Fetched: {url}")
            except Exception as page_error:
                print(f"Error fetching {url}: {page_error}")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(combined_text)
        print(f"Saved combined content to: {file_path}")

        return scraped_texts

    except Exception as e:
        print(f"Main scrape error: {e}")
        return []


def get_store_path(store_name: str) -> str:
    """
    Generate a file path for a user's vector store based on the store name.

    Args:
        store_name (str): The name of the vector store.

    Returns:
        str: Full path to the vector store directory.
    """
    return os.path.join(VECTOR_STORE_DIR, store_name)


def store_exists(store_name: str) -> bool:
    """
    Check if a vector store already exists for a given user.

    Args:
        store_name (str): The name of the vector store.

    Returns:
        bool: True if store exists, False otherwise.
    """
    return os.path.exists(get_store_path(store_name))


def text_file(filename: str, data: str) -> str:
    """
    Save given text data into a temporary file.

    Args:
        filename (str): The base name for the file (without extension).
        data (str): The text content to write.

    Returns:
        str: The full path to the created text file.
    """
    filepath = os.path.join(TEMP_DIR, f'{filename}.txt')
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)
    return filepath


def store_vectors(text_data: str, store_name: str):
    """
    Embed and store text data in a vector store using FAISS for a specific user.

    Args:
        text_data (str): The raw text data to embed.
        store_name (str): The unique store name for the user.
    """
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    textfile = text_file(store_name, text_data)
    loader = TextLoader(textfile)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = splitter.split_documents(docs)
    persist_dir = get_store_path(store_name)
    vectorstore = FAISS.from_documents(splits, embedding)  
    vectorstore.save_local(persist_dir)
    os.remove(textfile)


def load_vectors(store_name: str):
    """
    Load an existing FAISS vector store for a specific user.

    Args:
        store_name (str): The name of the vector store.

    Returns:
        FAISS: The loaded vector store object.
    """
    persist_dir = get_store_path(store_name)
    embedding = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(persist_dir, embedding,allow_dangerous_deserialization=True)


def create_qa_chain(vector_store):
    """
    Create a RetrievalQA chain using the given vector store and Gemini model.

    Args:
        vector_store (FAISS): The loaded vector store object.

    Returns:
        RetrievalQA: A RetrievalQA chain ready for question-answering.
    """
    retriever = vector_store.as_retriever(search_type="similarity", k=4)
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2
    )
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )


# def create_chatbot(bot_name , url):
#     try:
#         internal_links = []
#         internal_links = scare 

        
#     expect:





def ask_rag(question: str, qa_chain):
    """
    Query the QA chain with a natural language question.

    Args:
        question (str): The user's question.
        qa_chain (RetrievalQA): The QA chain object.

    Returns:
        str: The response generated by the model.
    """
    response = qa_chain.invoke({"query": question})
    return response["result"].strip()


if __name__ == "__main__":
    # Test the RAG pipeline with a demo website and user
    store_name = "ameotech"
    website = "https://ameotech.com"

    # Step 1: Scrape
    scraped = scrape_website(website, store_name)

    # Step 2: Combine text
    scraped_file_path = os.path.join(SCRAPED_DATA_DIR, store_name, "combined_scrape.txt")
    with open(scraped_file_path, "r", encoding="utf-8") as f:
        combined_text = f.read()

    # Step 3: Store vectors
    store_vectors(combined_text, store_name)

    # Step 4: Load and query
    vector_store = load_vectors(store_name)
    qa_chain = create_qa_chain(vector_store)
    answer = ask_rag("What is the name of the company", qa_chain)

    print("Answer:", answer)




