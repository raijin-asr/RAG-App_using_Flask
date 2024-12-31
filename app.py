from flask import Flask, request, jsonify, render_template
from utils.pdf_processor import extract_pdf_text, split_text_into_chunks
from utils.faiss_manager import create_and_save_vector_store, load_vector_store
from utils.prompt_creator import create_prompt_template
from utils.gemini_api import query_gemini
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
