import pdfplumber
import google.genai as genai
from dotenv import load_dotenv
import os

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

api_key = os.getenv('AI_API_KEY')
client = genai.Client(api_key)

response = client.models.generate_content(
    model="gemini-2.0-flash-lite",
    contents=generate_flashcards(extract_text_from_pdf("exam.pdf"), num=5)
)

print(response.text)

