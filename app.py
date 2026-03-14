from flask import Flask, request, render_template
from flask_cors import CORS
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers import pipeline, set_seed
from transformers import BioGptTokenizer, BioGptForCausalLM

from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image

import io
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch


# now i have mistrlal model for chat 
# iam gonne add blip to process the image 
# i have biogpt for medical question answering but it is not working well so i will try mistral for that as well
# bio gpt is not for chat so i can combine both biogpt answer and mistral chat with user  of rag and the other for chat




app = Flask(__name__)
CORS(app)

#model_name = "facebook/blenderbot-400M-distill"
#model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
#tokenizer = AutoTokenizer.from_pretrained(model_name)

set_seed(42)


# Load BLIP-2 captioning model
blip_processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-6.7b")
blip_model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-6.7b",
    torch_dtype=torch.float16
)
blip_model = blip_model.to("cuda" if torch.cuda.is_available() else "cpu")


#model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
) 
#model = model.to("cuda" if torch.cuda.is_available() else "cpu")
#When device_map="auto" sees memory is tight, it starts offloading some Mistral layers to CPU to make room for BLIP-2. 
# Once some layers are on CPU and some on GPU, the model is in a "split" state — and then your manual .to("cuda") line tries to move

#model = BioGptForCausalLM.from_pretrained("microsoft/biogpt")
#tokenizer = BioGptTokenizer.from_pretrained("microsoft/biogpt")


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

#🔵 STEP 3 — Flask receives the request
#This function is triggered when JS calls /chatbot
conversation_history = []
@app.route('/chatbot', methods=['POST','GET'])
def handle_prompt():
    print("Received request")

    text_data = request.form.get('prompt','')  # Get the 'prompt' field from the form data sent by the frontend. If 'prompt' is not present, 
    image_file = request.files.get('image')  # Get the 'image' file from the form data sent by the frontend. If 'image' is not present, this will be None.
   
    input_text = text_data
    print(f"Received prompt: {input_text}")
    # Create conversation history string
    
    if image_file:
        print("image received, processing with BLIP...")
        image_bytes = image_file.read()  # Read the uploaded image file as bytes
        image = Image.open(io.BytesIO(image_bytes)).convert('RGB')  # Open the image using PIL and convert to RGB 
      
        # BLIP-2 can answer questions directly — no Mistral rewriting needed
        if input_text:
            prompt = f"Question: {input_text} Answer:"
        else:
            prompt = "describe the image in detail"
       



        blip_prompt_test = "the image shows  " # for now we will use a fixed prompt to blip as the rewriting is not working well and sometimes it generates weird prompts , 
        
        print("----------BLIP2 is eating this  ---")
        print(prompt)
  



        # STEP 2 -------Process the image with BLIP using the rewritten prompt
        inputs = blip_processor(image, prompt, return_tensors="pt").to(blip_model.device,torch.float16)
        output = blip_model.generate(**inputs , max_new_tokens=200) 

        full_output = blip_processor.decode(output[0], skip_special_tokens=True).strip()
        #caption = full_output.replace(blip_prompt_test, "").strip()
        print(f"Clean caption: {full_output}")
        
        #return full_output






        #STEP 3 - now we gonna send that caption to mistral to make it more conversational and add some details to it and make it more like a response to the user question rather than a plain caption
       
        final_messages = [
            {"role": "system", "content": "You are a helpful assistant. You will be given an image description and the user's question. Respond directly and conversationally based only on the description provided. Do not add details that are not in the description."},
            {"role": "user", "content": f"Image description: '{full_output}'. User question: '{input_text if input_text else 'describe this image'}'."}
        ]
        mistral_messages = tokenizer.apply_chat_template(final_messages, return_tensors="pt", return_dict=True)
        mistral_messages = {k: v.to(model.device) for k, v in mistral_messages.items()}
        final_output = model.generate(
         **mistral_messages,
         max_new_tokens=200,
         do_sample=True,
          temperature=0.7,
          top_p=0.9
               )
        final_tokens = final_output[0][mistral_messages['input_ids'].shape[1]:]
        response = tokenizer.decode(final_tokens, skip_special_tokens=True).strip()
        print(f"Final Mistral response: {response}")

        return response
    else : 
        MAX_TURNS = 4
        #prompt = f"Answer the following medical question clearly:\n{input_text}\nAnswer:"
        history_string = "\n".join(conversation_history[-MAX_TURNS:]) + f"\nUser: {input_text}"

        print(f"Prompt: {input_text}")
        #prompt = f"[INST] You are a my friend and your name is mike.\n{input_text} [/INST]"
        messages = [
        {"role": "system", "content": "You are a my friend and your name is mike and this is what we talked about before -- "+history_string+"--so use it as a context to answer me."},
        {"role": "user", "content": input_text}
        ]

        #prompt = f"[INST] {input_text} [/INST]"
        inputs = tokenizer.apply_chat_template(messages, return_tensors="pt",return_dict=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        # Generate the response from the model
        output = model.generate(
            **inputs,
            max_new_tokens=100,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

        # ✅ Only new tokens (important!)
        generated_tokens = output[0][inputs['input_ids'].shape[1]:]
        # max_length will cause the model to crash at some point as history grows
        # Decode the response
        response = tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
        # Add interaction to conversation history
        conversation_history.append(f"User: {input_text}")
        conversation_history.append(f"Assistant: {response}")

        # 🔁 STEP 9 — Send response back -------
        return response
if __name__ == '__main__':
    app.run()



