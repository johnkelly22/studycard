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

def generate_flashcards(text, num=10):
    prompt = f"""Please read the following text and create EXACTLY {num} flashcard(s) in this format. Do not generate any additional text or explanations. Each flashcard should have a question and an answer, and they should be separated by exactly one newline:
Q: question
A: answer

TEXT:
{text}
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

    # Try to get the `num` parameter from the form data
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
    lines = raw_text.strip().split("\n")
    for i in range(0, len(lines), 2):
        if i+1 < len(lines) and lines[i].startswith("Q:") and lines[i+1].startswith("A:"):
            question = lines[i][2:].strip()
            answer = lines[i+1][2:].strip()
            flashcards.append({'q': question, 'a': answer})
    return flashcards

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
