from flask import Flask, render_template, request, jsonify, session
import os
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from fuzzywuzzy import process
from io import StringIO
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Set the HuggingFace API token
sec_key = os.getenv('HUGGINGFACEHUB_API_TOKEN')
os.environ["HUGGINGFACEHUB_API_TOKEN"] = sec_key

# Google Sheet details
file_id = '1Dt1Zud6fLTiNRx-_r7EaPiHAhQDcfcK5M9xxhX0x--Q'  # Replace with your actual file ID
sheet_gid = '1023326500'  # Replace with your actual sheet GID
url = f'https://docs.google.com/spreadsheets/d/{file_id}/export?format=csv&id={file_id}&gid={sheet_gid}'

documents = []
vectorstore = None

# Function to fetch Google Sheets data
def fetch_google_sheet_data():
    global documents, vectorstore
    response = requests.get(url)
    response.raise_for_status()

    csv_data = StringIO(response.text)
    custom_data = pd.read_csv(csv_data)

    # Create documents for each entry
    documents = [Document(page_content=f"Q: {row['Question']} A: {row['Answer']}") for index, row in custom_data.iterrows()]

    # Load documents into Chroma vector store
    embedding_function = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vectorstore = Chroma.from_documents(documents, embedding=embedding_function)

# Initial data load
fetch_google_sheet_data()

# Schedule data refresh every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_google_sheet_data, 'interval', minutes=3)
scheduler.start()

# Custom retrieval function
def custom_retrieval(question, documents, threshold=80):
    doc_questions = [doc.page_content.split(' A: ')[0].replace('Q: ', '') for doc in documents]
    best_match, score = process.extractOne(question, doc_questions)

    if score < threshold:
        return None
    
    best_match_index = doc_questions.index(best_match)
    return documents[best_match_index]

# Improved generate_step_by_step_answer function
def generate_step_by_step_answer(context, start=0, step_size=5):
    steps = [step.strip() for step in context.page_content.split('\n') if step.strip()]
    end = min(start + step_size, len(steps))
    chunk = steps[start:end]
    formatted_chunk = "<br><br>".join(chunk)
    return formatted_chunk, end < len(steps)

@app.route('/')
def home():
    return render_template('index.html')

# API route for answering questions
@app.route('/api', methods=['POST'])
def api():
    data = request.get_json()
    question = data.get('message')
    
    context = custom_retrieval(question, documents)
    
    if context:
        answer, has_more = generate_step_by_step_answer(context)
        session['full_answer'] = context.page_content
        session['last_step'] = 5  # Show the first 5 steps
        return jsonify({
            'message': answer,
            'has_more': has_more
        })
    
    return jsonify({
        'message': "I'm sorry, I couldn't find an answer for that question.",
        'has_more': False
    })

# API route for reading more steps
@app.route('/api/read_more', methods=['POST'])
def read_more():
    last_step = session.get('last_step', 0)
    context_content = session.get('full_answer', '')
    
    if context_content:
        context = Document(page_content=context_content)
        next_chunk, has_more = generate_step_by_step_answer(context, start=last_step)
        
        if next_chunk:
            session['last_step'] = last_step + 5  # Increment by 5 steps
            return jsonify({
                'message': next_chunk,
                'has_more': has_more
            })
    
    return jsonify({
        'message': "No more steps.",
        'has_more': False
    })

# Run the Flask app

#HUGGINGFACEHUB_API_TOKEN="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"
# FLASK_SECRET_KEY=flask_secret_key
if __name__ == '__main__':
    app.run(debug=True, port=9090)

######new changes
