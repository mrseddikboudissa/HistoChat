from flask import Flask, request, render_template
from flask_cors import CORS
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

app = Flask(__name__)
CORS(app)

model_name = "facebook/blenderbot-400M-distill"
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
conversation_history = []


    
@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')


@app.route('/chatbot', methods=['POST','GET'])
def handle_prompt():
    print("Received request")

    data = request.get_data(as_text=True)
    data = json.loads(data)
    input_text = data['prompt']
    print(f"Received prompt: {input_text}")
    # Create conversation history string
    history = "\n".join(conversation_history)
        
    history_string = "\n".join(conversation_history) + f"\nUser: {input_text}"
    print(history_string)
    inputs = tokenizer.encode_plus(history_string, return_tensors="pt")
    # Generate the response from the model
    output = model.generate(**inputs, use_cache=False)
  # max_length will cause the model to crash at some point as history grows
    # Decode the response
    response = tokenizer.decode(output[0], skip_special_tokens=True).strip()
    # Add interaction to conversation history
    conversation_history.append(input_text)
    conversation_history.append(response)
    return response
if __name__ == '__main__':
    app.run()



# this project is very importatn , take it as it is , and add my modiciation adn mytouch so that it can be more personalized and more like me 
#  1- i need to draw the full diagram of the project and how the data is flowing from the frontend to the backend and how the backend is processing the data and how it is sending the response back to the frontend 
# 2- i need to add more features to the chatbot like adding a database to store the conversation history and the user information and use it to personalize the responses of the chatbot
# 3- i need to add more functionalities to the chatbot like adding a feature to allow the user to upload a file and the chatbot can read the file and extract information from it and use
# 4- it to answer the user's questions
# 5- also it can be fine tuned to answer the questions related to a specific domain like medical or legal or any other domain that i want to specialize in
# 6- i can use langchain to create a more complex and more powerful chatbot that can handle more complex conversations and can integrate with other services and APIs to provide more functionalities to the users
# 7- i can use rag to create a more powerful chatbot that can retrieve information from a large knowledge base and use it to answer the user's questions in a more accurate and more relevant way

#8- 