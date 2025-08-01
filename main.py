from flask import Flask, request, jsonify
from flask_cors import CORS
import pdfplumber
import google.genai as genai
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
CORS(app)

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def generate_flashcards(text, num):
    prompt = f"""
    You are an expert flashcard generator.

    Please create exactly {num} flashcards based on the text below.
    Ensure you created EXACTLY {num} flashcards! After generating the flashcards, go back and check that you have created the correct number of flashcards.

    Each flashcard must have a question and an answer, formatted exactly as:

    Q: [question text]
    A: [answer text]

    Do NOT add any explanations or extra text.

    Here is the text to use:

    {text}

    Generate the flashcards now.
    """

    return prompt

key = os.getenv('AI_API_KEY')
client = genai.Client(api_key=key)

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Try to get the num parameter from the form data
    num = request.form.get('num', default=5, type=int)

    # Save the uploaded file temporarily
    temp_path = f"/tmp/{file.filename}"
    file.save(temp_path)

    # Extract text from PDF
    text = extract_text_from_pdf(temp_path)

    # Call Gemini API to generate flashcards
    prompt = generate_flashcards(text, num=num)
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )

    os.remove(temp_path)

    flashcards = parse_flashcards(response.text)
    return jsonify({'flashcards': flashcards})


def parse_flashcards(raw_text):
    flashcards = []
    lines = [line.strip() for line in raw_text.strip().split("\n") if line.strip()]  # remove empty lines
    question = None
    for line in lines:
        if line.startswith("Q:"):
            question = line[2:].strip()
        elif line.startswith("A:") and question is not None:
            answer = line[2:].strip()
            flashcards.append({'q': question, 'a': answer})
            question = None
    return flashcards

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)