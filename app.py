from flask import Flask, request, render_template
from flask_cors import CORS
from chat import chat_with_mistral
from vision import answer_image_question
from pdfreader import process_document, answer_document_question

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/chatbot', methods=['POST', 'GET'])
def handle_prompt():
    print("Received request")

    input_text = request.form.get('prompt', '')
    image_file = request.files.get('image')

    print(f"Received prompt: {input_text}")

    if image_file:
        return answer_image_question(image_file, input_text)
    else:
        return chat_with_mistral(input_text)

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    print("PDF upload received")
    
    pdf_file = request.files.get('pdf')
    
    if not pdf_file:
        return "No PDF file received", 400
    
    result = process_document(pdf_file)
    return result


@app.route('/ask_pdf', methods=['POST'])
def ask_pdf():
    print("PDF question received")
    
    question = request.form.get('prompt', '')
    
    if not question:
        return "No question received", 400
    
    response = answer_document_question(question)
    return response


if __name__ == '__main__':
    app.run()