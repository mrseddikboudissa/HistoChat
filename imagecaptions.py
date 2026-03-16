import torch
import io
from PIL import Image
from models import blip_model, blip_processor, mistral_model, mistral_tokenizer

def answer_image_question(image_file, input_text):
    # Read and convert image
    image_bytes = image_file.read()
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')

    # Build BLIP-2 prompt
    if input_text:
        blip_prompt = f"Question: {input_text} Answer:"
    else:
        blip_prompt = "the image shows"

    print(f"BLIP-2 prompt: {blip_prompt}")

    # BLIP-2 answers the question
    inputs = blip_processor(image, blip_prompt, return_tensors="pt").to(blip_model.device, torch.float16)
    output = blip_model.generate(**inputs, max_new_tokens=200)
    blip_answer = blip_processor.decode(output[0], skip_special_tokens=True).strip()

    print(f"BLIP-2 answer: {blip_answer}")

    # Mistral makes it conversational
    final_messages = [
        {"role": "system", "content": "You are a helpful assistant. You will be given an image description and the user's question. Respond directly and conversationally based only on the description provided. Do not add details that are not in the description."},
        {"role": "user", "content": f"Image description: '{blip_answer}'. User question: '{input_text if input_text else 'describe this image'}'."}
    ]

    mistral_inputs = mistral_tokenizer.apply_chat_template(final_messages, return_tensors="pt", return_dict=True)
    mistral_inputs = {k: v.to(mistral_model.device) for k, v in mistral_inputs.items()}

    final_output = mistral_model.generate(
        **mistral_inputs,
        max_new_tokens=200,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

    final_tokens = final_output[0][mistral_inputs['input_ids'].shape[1]:]
    response = mistral_tokenizer.decode(final_tokens, skip_special_tokens=True).strip()

    print(f"Final response: {response}")
    return response