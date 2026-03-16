import torch
import fitz  # PyMuPDF - for reading PDFs
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from models import mistral_model, mistral_tokenizer

print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cuda" if torch.cuda.is_available() else "cpu"}
)
print("Embedding model loaded!")

def extract_text_from_pdf(pdf_file):
    print("Extracting text from PDF...")
    
    # Read the uploaded file bytes
    pdf_bytes = pdf_file.read()
    
    # Open the PDF from bytes using PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    full_text = ""
    for page_num, page in enumerate(doc):
        text = page.get_text()
        full_text += f"\n--- Page {page_num + 1} ---\n{text}"
    
    print(f"Extracted {len(full_text)} characters from {len(doc)} pages")
    doc.close()
    return full_text

def chunk_text(full_text):
    print("Chunking text...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunks = text_splitter.split_text(full_text)
    print(f"Created {len(chunks)} chunks")
    return chunks

def create_vector_store(chunks):
    print("Embedding chunks and storing in Chroma...")
    
    vector_store = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory="./chroma_db"
    )
    
    print(f"Stored {len(chunks)} chunks in Chroma")
    return vector_store




def retrieve_relevant_chunks(vector_store, question, k=4):
    print(f"Retrieving top {k} chunks for question: {question}")
    
    retriever = vector_store.as_retriever(
        search_type="mmr", # mmr means Maximal Marginal Relevance, if two chunks say almost the same thing it picks the more diverse one instead. 
        search_kwargs={
            "k": k,
            "lambda_mult": 0.25 #controls that balance — closer to 0 means more diversity, closer to 1 means more similarity
        }
    )
    
    relevant_docs = retriever.invoke(question)
    chunks_text = "\n\n".join([doc.page_content for doc in relevant_docs])
    
    print(f"Retrieved {len(relevant_docs)} chunks")
    return chunks_text

def answer_from_document(question, chunks_text):
    print("Sending retrieved chunks to Mistral...")
    
    prompt = f"""Use the following context to answer the question.
If the answer is not available in the context, say "I don't know based on the provided document".
If the question is not related to the context, say "This question is not related to the document".

Context:
{chunks_text}

Question: {question}"""

    messages = [
        {"role": "system", "content": "You are a helpful assistant that answers questions based strictly on the provided context. Do not add information from outside the context."},
        {"role": "user", "content": prompt}
    ]

    inputs = mistral_tokenizer.apply_chat_template(
        messages,
        return_tensors="pt",
        return_dict=True
    )
    inputs = {k: v.to(mistral_model.device) for k, v in inputs.items()}

    output = mistral_model.generate(
        **inputs,
        max_new_tokens=300,
        do_sample=True,
        temperature=0.7,
        top_p=0.9
    )

    generated_tokens = output[0][inputs['input_ids'].shape[1]:]
    response = mistral_tokenizer.decode(generated_tokens, skip_special_tokens=True).strip()
    print(f"Mistral RAG response: {response}")
    return response



def process_document(pdf_file):
    global vector_store
    full_text = extract_text_from_pdf(pdf_file)
    chunks = chunk_text(full_text)
    vector_store = create_vector_store(chunks)
    return "Document processed successfully! You can now ask questions about it."

def answer_document_question(question):
    global vector_store
    if vector_store is None:
        return "Please upload a document first before asking questions."
    chunks_text = retrieve_relevant_chunks(vector_store, question)
    return answer_from_document(question, chunks_text)