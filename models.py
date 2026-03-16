import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from transformers import set_seed
from transformers import AutoProcessor, AutoModelForCausalLM
from transformers import pipeline


set_seed(42)

"""
print("Loading BLIP-2...")
# Load BLIP-2 captioning model
blip_processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-6.7b")
blip_model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-6.7b",
    torch_dtype=torch.float16
)
blip_model = blip_model.to("cuda" if torch.cuda.is_available() else "cpu")
print("BLIP-2 loaded!")"""


print("Loading Mistral...")

#model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
mistral_model_name = "mistralai/Mistral-7B-Instruct-v0.1"
mistral_tokenizer = AutoTokenizer.from_pretrained(mistral_model_name)
mistral_model = AutoModelForCausalLM.from_pretrained(
    mistral_model_name,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto"
) 
print("Mistral loaded!")

