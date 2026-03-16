from models import mistral_model, mistral_tokenizer

conversation_history = []

def chat_with_mistral(input_text):
    MAX_TURNS = 4
    history_string = "\n".join(conversation_history[-MAX_TURNS:])

    messages = [
        {"role": "system", "content": "You are a helpful assistant. This is what we talked about before: " + history_string},
        {"role": "user", "content": input_text}
    ]

    inputs = mistral_tokenizer.apply_chat_template(messages, return_tensors="pt", return_dict=True)
    inputs = {k: v.to(mistral_model.device) for k, v in inputs.items()}

    output = mistral_model.generate(
        **inputs,
        max_new_tokens=100,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

    generated_tokens = output[0][inputs['input_ids'].shape[1]:]
    response = mistral_tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()

    conversation_history.append(f"User: {input_text}")
    conversation_history.append(f"Assistant: {response}")

    return response