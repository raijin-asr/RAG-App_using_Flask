from flask import Flask, request, jsonify, render_template
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import google.generativeai as genai 

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index_RAG.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    if 'pdf_files' not in request.files:
        return jsonify({"error": "No PDF files provided"}), 400

    pdf_files = request.files.getlist('pdf_files')
    raw_text = extract_pdf_text(pdf_files)
    text_chunks = split_text_into_chunks(raw_text)
    create_and_save_vector_store(text_chunks)
    
    return jsonify({"message": "PDF processing completed successfully."})

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    user_question = data.get("question", "")

    if not user_question:
        return jsonify({"error": "Question is required"}), 400

    # Load FAISS vector store
    vector_store = load_vector_store()

    # Perform similarity search
    docs = vector_store.similarity_search(user_question)
    context = "\n\n".join([doc.page_content for doc in docs])

    # Create prompt and query Gemini API
    prompt = create_prompt_template()
    formatted_prompt = prompt.format(context=context, question=user_question)
    response = query_gemini(formatted_prompt)

    return jsonify({"question": user_question, "response": response})

def extract_pdf_text(pdf_docs):
    """Extract text from a list of PDF files."""
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def split_text_into_chunks(text):
    """Split large text into smaller chunks for processing."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=500)
    chunks = text_splitter.split_text(text)
    return chunks

def create_and_save_vector_store(text_chunks):
    """Create and save a vector store using HuggingFace embeddings."""
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")

def load_vector_store():
    """Load a saved FAISS vector store."""
    return FAISS.load_local("faiss_index")

def create_prompt_template():
    """Create a prompt template for querying Gemini."""
    prompt_template = """
    Answer the question as detailed as possible from the provided context. If the answer contains any structured data like tables or lists, respond in the same format. 
    If the answer is not in the provided context, just say, "The answer is not available in the context." Do not provide a wrong answer.

    Context:
    {context}

    Question:
    {question}
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=['context', 'question'])
    return prompt 

def query_gemini(prompt):
    """Query the Gemini API using the formatted prompt."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text if response and response.text else "No response generated."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
